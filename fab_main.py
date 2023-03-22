# main.py

# Standard library
import os
import sys

# Third part libraries
from discord.ext import commands

# Our libraries
from fab_bot import FabBot
import utils.logger as logger


def get_token():
    """ Reads the token file and strips whitespace and newlines """
    token = None
    k_token_file_name = "token.txt"
    file_path = os.path.join(os.path.dirname(__file__), k_token_file_name)

    try:
        with open(file_path) as token_file:
            token = token_file.read().strip(" \t\n\r")
        return token
    except FileNotFoundError:
        print(
            "{0} not found. Make sure it is in the same directory as main.py.".
            format(k_token_file_name))
        return token


token = get_token()
if not token:
    sys.exit()

logger.info("Starting Bot...")
bot = FabBot()


@bot.command()
async def sync(ctx: commands.Context) -> None:
    """ Sync slash commands """
    await ctx.bot.tree.sync()


bot.run(token)
logger.info("Stopped Bot")
