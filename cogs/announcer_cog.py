# announce_cog.py

# Standard library
import asyncio
import os
import pathlib

# Third party libaries
import discord
from discord.ext import commands
import yaml

# Our libraries
from tts_lib.audio_generator import AudioGenerator
from tts_lib.gtts_audio import GTTSAudio
from tts_lib.gcloud_tts_audio import GcloudAudio
from tts_lib.ffmpeg_pcm_audio import FFmpegPCMAudio

k_rejoin_frequency = 60
k_default_voice = "uk male 1"
k_gtts_voice = "robot"
k_audio_dir = "audio_files"
k_config_dir = "configs"
k_user_to_name_file = "UsersToNames.yml"
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
        self._rejoin = True
        self._speak_names = False

        self._voice = None
        self._default_voice = None
        self._available_voices = list()

        self._audio_paths = dict()
        self._audio_generator = None
        self._available_generators = list()
        self._users = dict()

        self.__init_dir()
        self.__init_generators()

        self.read_configs()
        self.generate_initial_audio()

    def __init_dir(self):
        """ Creates the audio directory if it doesn't exist """
        self._audio_dir = pathlib.Path(
            os.path.abspath((os.path.join(os.path.dirname(__file__), "..",
                                          k_audio_dir))))
        self._audio_dir.mkdir(parents=True, exist_ok=True)

    def __init_generators(self):
        """ Registers the functionality of each generator """
        # The first generator in the list has the highest priority for defaults
        # and naming conflicts
        for Generator in AudioGenerator.__subclasses__():
            generator = Generator(self._audio_dir)
            if (generator.init_success):
                if self._audio_generator is None:
                    self._audio_generator = generator
                if self._default_voice is None:
                    self._default_voice = generator.default_voice
                self._available_voices.extend(generator.available_voices())
                self._available_generators.append(generator)

        self._change_voice(k_default_voice)

        if self._audio_generator is None:
            raise RuntimeError("No audio generator could be used.")
        if self._voice is None:
            raise RuntimeError("No voice has been set.")

    def __voice_help_str(self):
        voice_list = []
        for voice in self._available_voices:
            indicate_current = False
            if voice == self._voice:
                indicate_current = True

            if voice == self._default_voice:
                voice += " (default)"

            if indicate_current:
                voice = "**{0} <- selected**".format(voice)

            voice_list.append(voice)
        display_header = "type `fab voice <selection>` to change the voice.\n"
        "Available voices:\n  "
        display_list = "\n  ".join(voice_list)
        return str(display_header + display_list)

    def _change_voice(self, desired_voice):
        """ Changes the currently spoken voice.
            Returns a boolean indicating whether or not the voice was changed
        """
        if self._voice and (desired_voice == self._voice):
            return False

        for generator in self._available_generators:
            for voice in generator.available_voices():
                if desired_voice == voice:
                    if self._audio_generator != generator:
                        self._audio_generator = generator
                    self._voice = voice
                    self._audio_generator.set_voice(self._voice)
                    return True
        raise KeyError

    async def _rejoin_general(self):
        """ Join the General channel if flag is set """
        if not self._rejoin:
            return
        if self.bot.voice_clients:
            return
        voice_client = await self.bot.voice_channels["General"].connect(
            reconnect=False, timeout=1)
        await self.say_audio(voice_client, "hello")

    async def _periodic_rejoin(self):
        """ Run loop to trigger rejoins """
        while True:
            await asyncio.gather(asyncio.sleep(k_rejoin_frequency),
                                 self._rejoin_general())

    async def start_periodic_rejoin(self):
        """ Init the run loop """
        await self._periodic_rejoin()

    def _read_users(self):
        """ Loads special user configs """
        users_to_names_path = pathlib.Path(
            os.path.abspath((os.path.join(os.path.dirname(__file__), "..",
                                          k_config_dir, k_user_to_name_file))))
        with open(users_to_names_path, 'r') as users_to_names_file:
            self._users = yaml.safe_load(users_to_names_file)
            print(self._users)

    def read_configs(self):
        """ Reads the config files and loads them """
        self._read_users()

    def generate_initial_audio(self):
        """ Generates the backup audio to be played if something fails """
        for voice in self._available_voices:
            self._change_voice(voice)
            self.generate_audio_set("user")
            audio_path = self._audio_generator.generate_audio_file(
                "voice changed", "voice_changed")
            self._audio_paths[voice + "changed"] = audio_path
        self._change_voice(k_default_voice)

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
        # TODO(Phil): Remove this when the gcloud lib can say audio
        audio_bytes = self._audio_generator.generate_direct_audio(text)
        source = discord.PCMVolumeTransformer(
            FFmpegPCMAudio(audio_bytes, pipe=True))
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
        """ <channel> Join the voice channel specified in the command """
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
        if ctx.voice_client is not None:
            ctx.voice_client.stop()
            await self.say_audio(ctx.voice_client, "hello")

    @commands.command()
    async def disconnect(self, ctx):
        """ Disconnects from the current voice channel """
        if ctx.voice_client is not None:
            # TODO(Phil): Remove this when the gcloud lib can say audio
            await self.say_audio(ctx.voice_client, "bye")
            await ctx.voice_client.disconnect()

    @commands.command()
    async def say(self, ctx, *, text):
        """ <text> Speak some text to the channel """
        if (ctx.voice_client is None) or (not ctx.voice_client.is_connected()):
            await ctx.channel.send(
                "I'm not currently connected to a voice channel.")
            return
        await self.say_audio(ctx.voice_client, text)

    @commands.command()
    async def voice(self, ctx, *, text=""):
        """ <option> Change the voice used when speaking """
        if text == "":
            await ctx.channel.send(self.__voice_help_str())
            return

        text = text.lower()
        if text == "default":
            text = self._default_voice
        try:
            changed = self._change_voice(text)
            if changed:
                await self.play_audio_file(ctx.voice_client,
                                           self._audio_paths[text + "changed"])
        except KeyError:
            await ctx.channel.send("Voice not supported.")

    @commands.command()
    async def speak_names(self, ctx, *, text):
        """ <on/off> Speak the user names of messages in tts """
        if "on" in text:
            self._speak_names = True
        if "off" in text:
            self._speak_names = False

    async def parse_command(self, message):
        ctx = await self.bot.get_context(message)
        if (ctx.voice_client is None) or (not ctx.voice_client.is_connected()):
            return
        if message.channel.name == "tts" or message.channel.name == "📣tts":
            spoken_message = message.content
            if self._speak_names:
                if message.author.name in self._users:
                    user = self._users[message.author.name]
                    spoken_message = self._users[
                        "name"] + " said " + message.content

            await self.say_audio(ctx.voice_client, spoken_message)
