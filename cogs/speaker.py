"""
speaker.py
"""
# Standard library
import asyncio
from async_timeout import timeout

# Third party libaries
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext import tasks

# Our libraries
from lib.tts.audio_generator import AudioGenerator
from lib.tts.gcloud_tts_audio import GcloudAudio
from lib.tts.ffmpeg_pcm_audio import FFmpegPCMAudio
from utils import logger

k_rejoin_frequency = 60  # seconds
k_initial_channel = "test"
k_join_text = "Hi"
k_leave_text = "bye"

async def setup(bot: commands.Bot):
    """ Loads the speaker """
    await bot.add_cog(Speaker(bot))

async def teardown(bot: commands.Bot):
    """ unload ths speaker """
    await bot.remove_cog("Speaker")

class Speaker(commands.Cog):
    """ Speaks messages in the current voice channel.
    """
    def __init__(self, bot: commands.Bot) -> None:
        """ Class constructor """
        self._bot: commands.Bot = bot
        self._voice_client = None
        self._audio_generator = GcloudAudio()
        self._desired_channel = None
        self._message_queue = asyncio.Queue()
        self._audio_done = asyncio.Event()

        # Option flags
        self._rejoin = True

    async def async_init(self) -> None:
        """ Init async tasks """
        await self._bot.wait_until_ready()
        self._desired_channel = self._bot.normalized_voice_channel(k_initial_channel)
        self._rejoin_channel.start()

    @tasks.loop(seconds = k_rejoin_frequency)
    async def _rejoin_channel(self) -> None:
        """ Join the channel if flag is set """
        # Disable if flag is not set
        if not self._rejoin:
            return

        # Only rejoin if not connected
        if self._bot.voice_clients:
            return
        if self._desired_channel is None:
            return

        logger.info("Unexpected disconnect detected. Rejoining channel.")
        self._voice_client = await self._desired_channel.connect(
            reconnect=False, timeout=1)
        await self.speak_audio(k_join_text)

    async def audio_loop(self) -> None:
        """ Speaks the queued messages to the currently connected channel. """
        logger.info("Audio loop started")
        await self._bot.wait_until_ready()
        while not self._bot.is_closed():
            self._audio_done.clear()

            try:
                async with timeout(60):  # 1 minute
                    message = await self._message_queue.get()
            except asyncio.TimeoutError:
                continue

            if not self._voice_client:
                continue

            logger.debug("Playing message " + message)
            audio_bytes = self._audio_generator.generate_direct_audio(message)
            source = discord.PCMVolumeTransformer(
                FFmpegPCMAudio(audio_bytes, pipe=True))

            self._voice_client.play(source,
                    after=lambda _: self._bot.loop.call_soon_threadsafe(self._audio_done.set))
            await self._audio_done.wait()
            logger.debug("Done playing message.")
            source.cleanup()
        logger.info("Audio loop closed")

    async def speak_audio(self, text: str) -> None:
        """ Adds the text to the speaker queue. """
        await self._message_queue.put(text)

    @commands.hybrid_command()
    async def join(self, ctx: commands.Context, channel_name: str) -> None:
        """ <channel> Join the voice channel specified in the command """
        channel = self._bot.normalized_voice_channel(channel_name)
        if channel is None:
            await ctx.channel.send("Channel " + channel_name + " could not be found.")

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        self._voice_client = await channel.connect()
        if self._voice_client is None:
            logger.warning("Failed to join voice channel " + channel_name + ".")
            await ctx.channel.send("Failed to join voice channel " + channel_name + ".")
            return

        self._desired_channel = channel
        logger.info("Joined voice channel " + channel_name)
        await ctx.channel.send("Joined voice channel " + channel_name + ".")

        self._voice_client.stop()
        await self.speak_audio(k_join_text)

    @commands.hybrid_command()
    async def disconnect(self, ctx: commands.Context) -> None:
        """ Disconnects from the current voice channel """
        if self._voice_client is not None:
            await self.speak_audio(k_leave_text)
            await ctx.voice_client.disconnect()
            self._desired_channel = None

            logger.info("Disconnected from voice channel.")
            await ctx.channel.send("Disconnected from voice channel.")
        else:
            await ctx.channel.send(
                "I'm not currently connected to a voice channel.")
            logger.warning("disconnect failed: Not connected to a voice channel.")

    @commands.hybrid_command(name = "say")
    async def say(self, ctx: commands.Context, text: str) -> None:
        """ <text> Speak some text to the channel """
        if (self._voice_client is None) or (not self._voice_client.is_connected()):
            await ctx.channel.send(
                "I'm not currently connected to a voice channel.")
            logger.warning("say failed: Not connected to a voice channel.")
            return
        await self.speak_audio(text)

    @commands.hybrid_command(name = "stop")
    async def stop(self, ctx: commands.Context) -> None:
        """ Stops speaking immediately. """
        if self._voice_client is None:
            await ctx.channel.send(
                "I'm not currently connected to a voice channel.")
            logger.warning("say failed: Not connected to a voice channel.")
            return
        self._voice_client.stop()
