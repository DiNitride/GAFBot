import time

import discord
from discord.ext import commands


class Core:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """
        Pong
        """
        await ctx.send(f"Pong! :ping_pong: **{self.bot.latency * 1000:.0f}ms**")


def setup(bot):
    bot.add_cog(Core(bot))
