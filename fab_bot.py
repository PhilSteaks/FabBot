# fab_bot.py

# Standard library
import asyncio
import logging

# Third party libaries
import discord
from discord.ext import commands
from discord.ext.commands import Bot

# Our libraries
from cogs.announcer_cog import Announcer
from cogs.channel_monitor_cog import ChannelMonitor
from cogs.commands_cog import Commands
from message_parser import MessageParser

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


class FabBot(Bot):
    def __init__(self, *args, **kwargs):
        """ Class Constructor """
        intents = discord.Intents(members=True,
                                  voice_states=True,
                                  messages=True,
                                  message_content=True,
                                  guilds=True)
        super(FabBot, self).__init__(intents=intents,
                                     command_prefix=commands.when_mentioned_or(
                                         k_command_prefix_lower,
                                         k_command_prefix_upper),
                                     activity=discord.Game("fab help"),
                                     *args,
                                     **kwargs)

        self.voice_channels = dict()
        self.text_channels = dict()
        self.parser = MessageParser(self)
        self.announcer = Announcer(self)

    async def on_ready(self):
        """ What to do when the bot goes online """
        print("Connected as {0.name}, {0.id}".format(self.user))

        await self.register_cogs()

        # Create a hash table of all the channels on the server so we can
        # reference them by name
        for channel in self.get_all_channels():
            if channel.type == discord.ChannelType.text:
                self.text_channels[channel.name[1:]] = channel
                self.text_channels[channel.name] = channel
            if channel.type == discord.ChannelType.voice:
                self.voice_channels[channel.name[1:]] = channel
                self.voice_channels[channel.name] = channel
        for key, value in self.voice_channels.items():
            print(key)
        await self.announcer.start_periodic_rejoin()

        cog = self.get_cog('Announcer')
        commands = cog.get_commands()
        print([c.name for c in commands])

    async def on_message(self, message):
        """ What to do when a message is received on a text channel """
        logging.info(message)
        print(message)
        await self.parser.parse_command(message)
        await self.announcer.parse_command(message)

        # Needed to handle bot commands
        await self.process_commands(message)

    async def send_message(self, channel, message):
        """ A wrapper for sending messages """
        await channel.send(message)

    async def send_system_message(self, guild, message):
        """ Sends to the server's system channel. If not accessible, sends to a
            channel named "system". Does nothing if both fail.
        """
        channel = guild.system_channel
        if not can_send(channel):
            channel = self.text_channels["system"]
        if channel is None:
            print("Server {0.name}({0.id}) does not have a system channel.".
                  format(guild))
            return
        await self.send_message(channel, message)

    async def register_cogs(self):
        """ Registers the cogs that the bot will have """
        await self.add_cog(Commands(self))
        await self.add_cog(ChannelMonitor(self))
        await self.add_cog(self.announcer)
