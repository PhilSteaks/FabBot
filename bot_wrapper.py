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

@bot.event
async def on_message(message):
    if message.content == "test":
        await fab.send_message(message.channel, "Testing 1 2 3!")

    if "years ago" in message.content.lower():
        await fab.send_message(message.channel, "<Insert link from Nelson")

@bot.event
async def on_voice_state_update(member, before, after):
    await fab.log_user_channel_update(member, before, after)

def Start():
    fab.register(bot)
    fab.start()
