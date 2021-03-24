# bot_wrapper.py
from fab_bot import fab
import discord
from discord.ext.commands import Bot
from discord import Intents

intents = Intents.all()
bot = Bot(intents=intents, command_prefix='$')

@bot.event
async def on_ready():
    print("Bot is connected as {bot.user}")
    fab.real_init()

@bot.event
async def on_message(message):
    await fab.handle_message(message)

@bot.event
async def on_voice_state_update(member, before, after):
    await fab.log_user_channel_update(member, before, after)

def Start():
    fab.register(bot)
    fab.start()
