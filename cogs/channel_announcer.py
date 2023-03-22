"""
channel_announcer.py
"""
# Standard library
import asyncio

# Third party libaries
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext import tasks

# Our libraries
from utils import logger

async def setup(bot: commands.Bot):
    """ Loads the announcer """
    await bot.add_cog(ChannelAnnouncer(bot))

async def teardown(bot: commands.Bot):
    """ unload ths announcer """
    await bot.remove_cog("ChannelAnnouncer")

class ChannelAnnouncer(commands.Cog):
    """ Announces when someone leaves or joins the voice channel.
    """
    def __init__(self, bot: commands.Bot) -> None:
        """ Class constructor """
        self._bot: commands.Bot = bot

    async def async_init(self) -> None:
        """ Init async tasks """
        await self._bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """ What to do when someone leaves or joins a voice channel """
        voice_client = self._bot.current_voice_client()
        if voice_client is None:
            return

        # User joins the channel
        if after.channel is not None and before.channel is None:
            if after.channel is voice_client.channel:
                await self._bot.say_message(member + " has joined the channel.")
            return

        # User leaves the channel
        if before.channel is not None and after.channel is None:
            if before.channel is voice_client.channel:
                await self._bot.say_message(member + " has left the channel.")
            return

        # User switches channels
        if before.channel is not after.channel:
            if voice_client.channel is before.channel:
                await self._bot.say_message(member + " has left the channel.")
            if voice_client.channel is after.channel:
                await self._bot.say_message(member + " has joined the channel.")
            return
