# channel_monitor_cog.py

import discord
from discord.ext import commands

k_private_channels = ["Beyond FabSteaks", "[200~🥦Beyond FabSteaks"]


class ChannelLogger(commands.Cog):
    """ Cog to log when a user leaves """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """ What to do when someone leaves or joins a voice channel """
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
        if channel.name in k_private_channels or channel.name[
                1:] in k_private_channels:
            return

        await self.bot.send_system_message(
            channel.guild, "**%s** has disconnected from %s." %
            (member.display_name, channel.name))

    async def __log_user_join(self, member, channel):
        if channel.name in k_private_channels or channel.name[
                1:] in k_private_channels:
            return

        await self.bot.send_system_message(
            channel.guild, "**%s** has connected to %s." %
            (member.display_name, channel.name))

    async def __log_user_channel_switch(self, member, before, after):
        if before.guild.id == after.guild.id:
            if before.name in k_private_channels or before.name[
                    1:] in k_private_channels:
                return await self.__log_user_join(member, after)

            if after in self.private_channels or after.name[
                    1:] in k_private_channels:
                return await self.__log_user_leave(member, before)

            return await self.bot.send_system_message(
                before.guild, "**%s** has switched from **%s** to **%s**." %
                (member.display_name, before.name, after.name))
