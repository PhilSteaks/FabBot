# commands_cog.py
from discord.ext import commands
import discord


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author
        await ctx.send("Hello {0.name}~".format(member))

    @commands.command()
    async def ulous(self, ctx):
        await ctx.send("Thats right")
