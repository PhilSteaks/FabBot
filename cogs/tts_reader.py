"""
tts_reader.py
"""
# Standard library
import asyncio
import re

# Third party libaries
import discord
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext import tasks

# Our libraries
from utils import logger


async def setup(bot: commands.Bot):
    """ Loads the reader """
    await bot.add_cog(TtsReader(bot))


async def teardown(bot: commands.Bot):
    """ unload ths reader """
    await bot.remove_cog("TtsReader")


class TtsReader(commands.Cog):
    """ Speaks all messages written to the tts channel """
    def __init__(self, bot: commands.Bot) -> None:
        """ Class constructor """
        self._bot: commands.Bot = bot
        self._speak_names = False

    async def async_init(self) -> None:
        """ Init async tasks """
        await self._bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        voice_client = self._bot.current_voice_client()
        if voice_client is None:
            return

        if message.channel.name == "tts" or message.channel.name == "📣tts":
            spoken_message = message.content

            if self._speak_names:
                if message.author.name in self._users:
                    user = self._users[message.author.name]
                    spoken_message = self._users[
                        "name"] + " said " + message.content

            await self._bot.say_message(spoken_message)
