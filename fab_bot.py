import discord
from discord.ext.commands import Bot

k_system_channel_id = 737860696779259945
k_bot_token = "ODI0MTMxNjE5ODUyOTEwNjIy.YFq6YQ.ir_wi_s6sV3J95stoNtRrkzs0xg"

def member_display_text(member):
    return member.mention

class FabBot():
    def __init__(self):
        self.bot = None

    def register(self, bot_client):
        self.bot = bot_client

    def start(self):
        self.bot.run(k_bot_token)

    def send_message(self, channel, message):
        return channel.send(message)

    def send_system_message(self, message):
        system_channel = self.bot.get_channel(k_system_channel_id)
        return self.send_message(system_channel, message)

    def log_user_leave(self, member, channel):
        member_name = member_display_text(member)
        channel_name = channel.name
        return self.send_system_message("%s has left %s." % (member_name, channel_name))

    def log_user_join(self, member, channel):
        member_name = member_display_text(member)
        channel_name = channel.name
        return self.send_system_message("%s has joined %s." % (member_name, channel_name))

    def log_user_channel_switch(self, member, before, after):
        member_name = member_display_text(member)
        return self.send_system_message("%s has switched from %s to %s." % (
                member_name, before.name, after.name))

    def log_user_channel_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            return self.log_user_join(member, after.channel)
        if before.channel is not None and after.channel is None:
            return self.log_user_leave(member, before.channel)
        return self.log_user_channel_switch(member, before.channel, after.channel)

fab = FabBot()
