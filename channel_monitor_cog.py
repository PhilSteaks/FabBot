# channel_monitor_cog.py
from discord.ext import commands
import discord


class ChannelMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # User joins a channel
        if before.channel is None and after.channel is not None:
            return await self.__log_user_join(member, after.channel)

        # User leaves a channel
        if before.channel is not None and after.channel is None:
            return await self.__log_user_leave(member, before.channel)

        # User switches channels
        if before.channel is not after.channel:
            return await self.__log_user_channel_switch(
                member, before.channel, after.channel)
        return

    async def __log_user_leave(self, member, channel):
        await self.bot.send_system_message(
            channel.guild, "**%s** has disconnected from %s." %
            (member.display_name, channel.name))

    async def __log_user_join(self, member, channel):
        channel_name = channel.name
        await self.bot.send_system_message(
            channel.guild, "**%s** has connected to %s." %
            (member.display_name, channel.name))

    async def __log_user_channel_switch(self, member, before, after):
        if before.guild.id == after.guild.id:
            return await self.bot.send_system_message(
                before.guild, "**%s** has switched from **%s** to **%s**." %
                (member.display_name, before.name, after.name))
