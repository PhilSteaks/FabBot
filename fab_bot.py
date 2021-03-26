# fab_bot.py
import asyncio

from channel_monitor_cog import ChannelMonitor
from commands_cog import Commands
import discord
from discord.ext.commands import Bot
from message_parser import MessageParser

k_system_channel_id = 737860696779259945
k_default_voice_channel = "General"
k_bot_name = "FabBot"
k_command_prefix = "fab "


async def do_nothing():
    pass


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
        intents = discord.Intents(members=True,
                                  voice_states=True,
                                  messages=True,
                                  guilds=True)
        super(FabBot, self).__init__(intents=intents,
                                     command_prefix=k_command_prefix,
                                     *args,
                                     **kwargs)
        self.voice_channels = {}
        self.text_channels = {}
        self.responder = MessageParser(self)

    async def on_ready(self):
        print("Bot connected")
        for channel in self.get_all_channels():
            if channel.type == discord.ChannelType.text:
                self.text_channels[channel.name] = channel
            if channel.type == discord.ChannelType.voice:
                self.voice_channels[channel.name] = channel

    async def on_message(self, message):
        await self.responder.parse_command(message)
        await self.process_commands(message)

    async def send_message(self, channel, message):
        await channel.send(message)

    async def send_system_message(self, guild, message):
        channel = guild.system_channel
        if not can_send(channel):
            channel = self.text_channels["system"]
        if channel is None:
            print("Server %s(%d) does not have a system channel." %
                  (guild.name, guild.id))
            return
        await self.send_message(channel, message)

    def register_cogs(self):
        self.add_cog(Commands(self))
        self.add_cog(ChannelMonitor(self))
