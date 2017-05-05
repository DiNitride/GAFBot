from discord.ext import commands


class GAF:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def GAF(self, ctx):
        """Information on The Never Ending GAF"""
        await ctx.send("http://www.neverendinggaf.com")


def setup(bot):
    bot.add_cog(GAF(bot))