from discord.ext import commands
import discord

from utils import checks


class GAF:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def GAF(self, ctx):
        """Information on The Never Ending GAF"""
        await ctx.send("http://www.neverendinggaf.com")

    @commands.command()
    @checks.is_gaf_server()
    async def chill(self, ctx):
        """Channel 1 and chill?"""
        await ctx.send(content="<@&172426880543227904> <@&262334316611239937>", file=discord.File("media/chill.jpg"))
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(GAF(bot))