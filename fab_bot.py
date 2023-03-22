# fab_bot.py

# Standard library
import asyncio
import logging

# Third party libaries
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord import app_commands

# Our libraries
from cogs.channel_announcer import ChannelAnnouncer
from cogs.speaker import Speaker
from cogs.tts_reader import TtsReader
from cogs.channel_logger import ChannelLogger
from utils import logger

k_default_voice_channel = "General"
k_bot_name = "FabBot"
k_command_prefix_lower = "fab "
k_command_prefix_upper = "Fab "


def can_send(channel):
    """ Check if bot can send a message to a specific channel """
    if channel is None:
        return False
    for member in channel.members:
        if k_bot_name == member.name:
            return True
    return False

def normalized_channel(channel_dict, channel_name):
    """ Normalized channel names ignoring the emoji """
    if channel_name.lower() in channel_dict:
        return channel_dict[channel_name.lower()]
    if channel_name[1:].lower() in channel_dict:
        return channel_dict[channel_name[1:].lower()]

    logger.warning("Channel " + channel_name + " does not exist.")
    return None


class FabBot(Bot):
    """ Main bot class that holds the cogs """
    def __init__(self, *args, **kwargs):
        """ Class Constructor """
        intents = discord.Intents(members=True,
                                  voice_states=True,
                                  messages=True,
                                  message_content=True,
                                  guilds=True)
        super().__init__(intents=intents,
                                     command_prefix=commands.when_mentioned_or(
                                         k_command_prefix_lower,
                                         k_command_prefix_upper),
                                     activity=discord.Game("fab help"),
                                     *args,
                                     **kwargs)

        self.voice_channels = dict()
        self.text_channels = dict()
        self.speaker_cog = None

    def normalized_text_channel(self, channel_name):
        """ Normalized text channel names ignoring the emoji """
        return normalized_channel(self.text_channels, channel_name)

    def normalized_voice_channel(self, channel_name):
        """ Normalized voice channel names ignoring the emoji """
        return normalized_channel(self.voice_channels, channel_name)

    def current_voice_client(self):
        """ Returns the current voice client """
        if self.speaker_cog is None:
            logger.warning("Unable to retrieve voice client. Speaker cog is not loaded.")
            return None

        return self.speaker_cog.voice_client

    def _scan_channels(self):
        """ Scans the channels and adds them to be referenced later """
        # Create a hash table of all the channels on the server so we can
        # reference them by name
        for channel in self.get_all_channels():
            if channel.type == discord.ChannelType.text:
                self.text_channels[channel.name.lower()] = channel
                self.text_channels[channel.name[1:].lower()] = channel
            if channel.type == discord.ChannelType.voice:
                self.voice_channels[channel.name.lower()] = channel
                self.voice_channels[channel.name[1:].lower()] = channel

        for key, _ in self.voice_channels.items():
            logger.debug("Voice channels visible:\n" + key)
        for key, _ in self.text_channels.items():
            logger.debug("Text channels visible:\n" + key)

    async def _load_cogs(self):
        """ Loads and inits all the cogs """
        await self.add_cog(ChannelAnnouncer(self))
        await self.add_cog(TtsReader(self))
        await self.add_cog(ChannelLogger(self))

        self.speaker_cog = Speaker(self)
        await self.add_cog(self.speaker_cog)
        await self.speaker_cog.async_init()
        await self.loop.create_task(self.speaker_cog.audio_loop())

    async def setup_hook(self):
        """ Initial init """
        extension_list = [
                ]
        for extension in extension_list:
            await self.load_extension(extension)

    async def on_ready(self):
        """ What to do when the bot goes online """
        logger.info("Connected as {0.name}, {0.id}".format(self.user))

        self._scan_channels()
        await self._load_cogs()

    async def on_message(self, message):
        """ What to do when a message is received on a text channel """
        # Needed to handle bot commands
        await self.process_commands(message)

    async def send_message(self, channel, message):
        """ A wrapper for sending messages """
        text_channel = channel
        if text_channel is None:
            logger.warning("Text channel not found: " + channel)
            return

        await text_channel.send(message)

    async def send_system_message(self, guild, message):
        """ Sends to the server's system channel. If not accessible, sends to a
            channel named "system". Does nothing if both fail.
        """
        channel = guild.system_channel
        if not can_send(channel):
            channel = self.normalized_text_channel("system")
        if channel is None:
            logger.info("Server {0.name}({0.id}) does not have a system channel.".
                  format(guild))
            return
        await self.send_message(channel, message)

    async def say_message(self, message):
        """ A wrapper for saying voice messages """
        if self.speaker_cog is None:
            logger.warning("Unable to speak message. Speaker cog is not loaded.")
            return

        await self.speaker_cog.speak_audio(message)
