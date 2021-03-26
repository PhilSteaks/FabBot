# announce_cog.py

import os
import pathlib

from discord.ext import commands
import discord

from gtts_audio import GTTSAudio

k_audio_dir = "audio_files"
join_message_template = "{0} has joined the channel."
leave_message_template = "{0} has left the channel."
switch_message_template = "{0} has switched channels."
join_hint_template = "{0}_join"
leave_hint_template = "{0}_leave"
switch_hint_template = "{0}_switch"

class Announcer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._audio_dir = None
        self._audio_generator = None

        self.__init_dir()
        self._audio_generator = GTTSAudio(self._audio_dir)
        self._audio_paths = {}

        self.generate_initial_audio()

    def __init_dir(self):
        self._audio_dir = pathlib.Path(
            os.path.abspath((os.path.join(os.path.dirname(__file__), k_audio_dir))))
        self._audio_dir.mkdir(parents=True, exist_ok=True)

    def generate_initial_audio(self):
        self.generate_audio_set("user")

    def generate_member_audio(self, member):
        return self.generate_audio_set(member.display_name)

    def generate_audio_set(self, name):
        join_message = join_message_template.format(name)
        leave_message = leave_message_template.format(name)
        switch_message = switch_message_template.format(name)
        join_hint = join_hint_template.format(name)
        leave_hint = leave_hint_template.format(name)
        switch_hint = switch_message_template.format(name)

        join_path = self._audio_generator.generate_audio(
            join_message, join_hint)
        leave_path = self._audio_generator.generate_audio(
            leave_message, leave_hint)
        switch_path = self._audio_generator.generate_audio(
            switch_message, switch_hint)

        self._audio_paths[name] = {
            "join": join_path,
            "leave": leave_path,
            "switch": switch_path
        }

    async def play_audio(self, audio_file):
        pass

    async def announce_update(self, member, update):
        key = member.display_name
        if key not in self._audio_paths:
            self.generate_member_audio(member)

        # default to fallback audio if unable to generate the audio
        if key not in self._audio_paths:
            key = "user"

        if update in self._audio_paths[key]:
            await self.play_audio(self._audio_paths[key][update])

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # User joins a channel
        if before.channel is None and after.channel is not None:
            await self.announce_update(member, "join")
            return

        # User leaves a channel
        if before.channel is not None and after.channel is None:
            await self.announce_update(member, "leave")
            return

        # User switches channels
        if before.channel is not after.channel:
            await self.announce_update(member, "switch")
            return

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()

    @commands.command()
    async def disconnect(self, ctx):
        await ctx.voice_client.disconnect()
