# announce_cog.py

# Standard library
import os
import pathlib

# Third party libaries
import discord
from discord.ext import commands

# Our libraries
from tts_lib.gtts_audio import GTTSAudio
from tts_lib.gcloud_tts_audio import GcloudAudio
from tts_lib.ffmpeg_pcm_audio import FFmpegPCMAudio

k_default_voice = "female 3"
k_gtts_voice = "robot"
k_audio_dir = "audio_files"
join_message_template = "{0} has joined the channel."
leave_message_template = "{0} has left the channel."
switch_message_template = "{0} has switched channels."
join_hint_template = "{0}_join"
leave_hint_template = "{0}_leave"
switch_hint_template = "{0}_switch"


class Announcer(commands.Cog):
    def __init__(self, bot):
        """ Class Constructor"""
        # Good practice to declare all the variables you'll use here.
        # So they'll still be defined in case the remaining init methods fail
        self.bot = bot
        self._audio_dir = None
        self._audio_generator = None

        self.__init_dir()
        self._audio_generator = GcloudAudio(self._audio_dir)
        self._voice = k_default_voice
        self._audio_paths = dict()
        self._available_voices = self._audio_generator.available_voices()
        self._available_voices.append(k_gtts_voice)

        self.generate_initial_audio()

    def __init_dir(self):
        """ Creates the audio directory if it doesn't exist """
        self._audio_dir = pathlib.Path(
            os.path.abspath((os.path.join(os.path.dirname(__file__), "..",
                                          k_audio_dir))))
        self._audio_dir.mkdir(parents=True, exist_ok=True)

    def generate_initial_audio(self):
        """ Generates the backup audio to be played if something fails """
        self.generate_audio_set("user")
        for voice in self._available_voices:
            if voice == k_gtts_voice:
                continue
            self._audio_generator.set_voice(voice)
            audio_path = self._audio_generator.generate_audio_file(
                "voice changed.", "voice_changed")
            self._audio_paths[voice + "changed"] = audio_path
        self._audio_generator.set_voice(self._voice)

    def generate_member_audio(self, member):
        return self.generate_audio_set(member.display_name)

    def generate_audio_set(self, name):
        """ Generates all the audio files associated for a specific user """
        join_message = join_message_template.format(name)
        leave_message = leave_message_template.format(name)
        switch_message = switch_message_template.format(name)
        join_hint = join_hint_template.format(name)
        leave_hint = leave_hint_template.format(name)
        switch_hint = switch_hint_template.format(name)

        join_path = self._audio_generator.generate_audio_file(
            join_message, join_hint)
        leave_path = self._audio_generator.generate_audio_file(
            leave_message, leave_hint)
        switch_path = self._audio_generator.generate_audio_file(
            switch_message, switch_hint)

        self._audio_paths[name + self._audio_generator.prefix] = {
            "join": join_path,
            "leave": leave_path,
            "switch": switch_path
        }

    async def say_audio(self, voice_client, text):
        io = self._audio_generator.generate_direct_audio(text)
        source = discord.PCMVolumeTransformer(
            FFmpegPCMAudio(io.read(), pipe=True))
        voice_client.play(source)

    async def play_audio_file(self, voice_client, audio_file):
        if voice_client is None:
            return
        if voice_client.is_connected():
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(audio_file))
            voice_client.play(source)

    async def announce_update(self, voice_client, member, update):
        key = member.display_name + self._audio_generator.prefix
        if key not in self._audio_paths:
            self.generate_member_audio(member)

        # default to fallback audio if unable to generate the audio
        if key not in self._audio_paths:
            key = "user"

        if update in self._audio_paths[key]:
            await self.play_audio_file(voice_client,
                                       self._audio_paths[key][update])

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """ What to do when someone leaves or joins a voice channel """
        # User joins a channel
        if before.channel is None and after.channel is not None:
            voice_client = after.channel.guild.voice_client
            if voice_client is not None:
                if voice_client.channel is after.channel:
                    await self.announce_update(voice_client, member, "join")
            return

        # User leaves a channel
        if before.channel is not None and after.channel is None:
            voice_client = before.channel.guild.voice_client
            if voice_client is not None:
                if voice_client.channel is before.channel:
                    await self.announce_update(voice_client, member, "leave")
            return

        # User switches channels
        if before.channel is not after.channel:
            voice_client = before.channel.guild.voice_client
            if voice_client is not None:
                if voice_client.channel is before.channel:
                    await self.announce_update(voice_client, member, "switch")
                if voice_client.channel is after.channel:
                    await self.announce_update(voice_client, member, "join")
            return

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """ Join the voice channel specified in the command """
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
        if ctx.voice_client is not None:
            ctx.voice_client.stop()
            if self._voice == k_gtts_voice:
                await self.say_audio(ctx.voice_client, "Hello.")

    @commands.command()
    async def disconnect(self, ctx):
        """ Disconnects from the current voice channel """
        if ctx.voice_client is not None:
            await self.say_audio(ctx.voice_client, "Goodbye.")
            await ctx.voice_client.disconnect()

    @commands.command()
    async def say(self, ctx, *, text):
        """ Speak some text to the channel """
        if (ctx.voice_client is None) or (not ctx.voice_client.is_connected()):
            await ctx.channel.send(
                "I'm not currently connected to a voice channel.")
            return

        if self._voice != k_gtts_voice:
            await ctx.channel.send(
                "Only supported with `{0}` voice for now. Type \"fab voice\" for more information."
                .format(k_gtts_voice))
            return

        await self.say_audio(ctx.voice_client, text)

    @commands.command()
    async def voice(self, ctx, *, text=""):
        """ Speak some text to the channel """
        if text == "":
            voice_list = []
            for voice in self._available_voices:
                if voice == "default":
                    continue

                if voice == k_default_voice:
                    if voice == self._voice:
                        voice = "**{0} (default)**".format(voice)
                    else:
                        voice += " (default)"
                elif voice == self._voice:
                    voice = "**{0}**".format(voice)

                voice_list.append(voice)
            display_header = "Available voices:\n  "
            display_list = "\n  ".join(voice_list)
            await ctx.channel.send(display_header + display_list)
            return

        text = text.lower()
        if text == "default":
            text = k_default_voice
        # Do nothing if already the current voice
        if text == self._voice:
            return

        if text == k_gtts_voice:
            self._audio_generator = GTTSAudio(self._audio_dir)
            self._voice = text
            await self.say_audio(ctx.voice_client, "voice changed.")
            return

        for voice in self._available_voices:
            if text == voice:
                if self._voice == k_gtts_voice:
                    # Switch generator if needed
                    self._audio_generator = GcloudAudio(self._audio_dir)

                self._audio_generator.set_voice(text)
                self._voice = text
                await self.play_audio_file(ctx.voice_client,
                                           self._audio_paths[text + "changed"])
                return
        await ctx.channel.send("Voice not supported.")
