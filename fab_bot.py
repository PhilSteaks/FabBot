# fab_bot.py
import asyncio

import discord
from discord.ext.commands import Bot
from message_responder import MessageResponder

k_system_channel_id = 737860696779259945
k_default_voice_channel = "General"
k_bot_token = "ODI0MTMxNjE5ODUyOTEwNjIy.YFq6YQ.PlIrW_VmGL-oS-kmgo3116BvlyI"


async def do_nothing():
    pass


def display_name(member):
    if member.nick:
        return member.nick
    return member.name


class FabBot():
    def __init__(self):
        self.bot = None
        self.voice_channels = {}
        self.text_channels = {}
        self.responder = MessageResponder(self)

    def register(self, bot_client):
        self.bot = bot_client

    def start(self):
        self.bot.run(k_bot_token)

    def real_init(self):
        for channel in self.bot.get_all_channels():
            if channel.type == discord.ChannelType.text:
                self.text_channels[channel.name] = channel
            if channel.type == discord.ChannelType.voice:
                self.voice_channels[channel.name] = channel

        self.join_voice(self.voice_channels[k_default_voice_channel])
        print("Bot started")

    def join_voice(self, channel):
        pass

    def send_message(self, channel, message):
        return channel.send(message)

    def send_system_message(self, message):
        system_channel = self.bot.get_channel(k_system_channel_id)
        return self.send_message(system_channel, message)

    def __log_user_leave(self, member, channel):
        return self.send_system_message("%s has disconnected from %s." %
                                        (display_name(member), channel.name))

    def __log_user_join(self, member, channel):
        member_name = member_display_text(member)
        channel_name = channel.name
        return self.send_system_message("%s has connected to %s." %
                                        (display_name(member), channel.name))

    def __log_user_channel_switch(self, member, before, after):
        return self.send_system_message(
            "%s has switched from %s to %s." %
            (display_name(member), before.name, after.name))

    def log_user_channel_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            return self.__log_user_join(member, after.channel)
        if before.channel is not None and after.channel is None:
            return self.__log_user_leave(member, before.channel)
        return self.__log_user_channel_switch(member, before.channel,
                                              after.channel)

    def handle_message(self, message):
        return self.responder.parse_command(message)


fab = FabBot()
