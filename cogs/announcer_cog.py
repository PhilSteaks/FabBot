# announce_cog.py

# Standard library
import os
import pathlib

# Third party libaries
import discord
from discord.ext import commands

# Our libraries
from tts_lib.gtts_audio import GTTSAudio

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
        self._audio_generator = GTTSAudio(self._audio_dir)
        self._audio_paths = dict()

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

        self._audio_paths[name] = {
            "join": join_path,
            "leave": leave_path,
            "switch": switch_path
        }

    async def say_audio(self, voice_client, text):
        io = self._audio_generator.generate_direct_audio(text)
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(io, pipe=True))
        voice_client.play(source)

    async def play_audio_file(self, voice_client, audio_file):
        if voice_client.is_connected():
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(audio_file))
            voice_client.play(source)

    async def announce_update(self, voice_client, member, update):
        key = member.display_name
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

    @commands.command()
    async def disconnect(self, ctx):
        """ Disconnects from the current voice channel """
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

    @commands.command()
    async def say(self, ctx, text):
        """ Speak some text to the channel """
        if (ctx.voice_client is None) or (not ctx.voice_client.is_connected()):
            ctx.channel.send("I'm not currently connected to a voice channel.")
            return

        await ctx.channel.send("I can't do this yet.")
        # await self.say_audio(ctx.voice_client, text)
