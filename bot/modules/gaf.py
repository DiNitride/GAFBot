from discord.ext import commands
import discord

from utils import checks


class GAF:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def gaf(self, ctx):
        """Information on The Never Ending GAF"""
        await ctx.send("The Never Ending GAF is a small group of idiots that play games and insult each other. "
                       "\nWe reside on our Discord server, usually in the beloved cesspool intelligently "
                       "titled \"Channel 1\".\nFeel free to pop by, probably get told to piss off, and maybe "
                       "play some games."
                       "\nMore info and invite links: <http://www.neverendinggaf.com>")

    @gaf.command()
    async def website(self, ctx):
        """Link to The Never Ending GAF's Website"""
        await ctx.send("<http://www.neverendinggaf.com>")

    @gaf.command()
    async def invite(self, ctx):
        """GAF Guild Invite"""
        await ctx.send("<http://discord.neverendinggaf.com>")

    @commands.command()
    @checks.is_gaf_server()
    async def chill(self, ctx):
        """Channel 1 and chill?"""
        await ctx.send(content="<@&172426880543227904> <@&262334316611239937>, chill? - {}".format(ctx.author), file=discord.File("resources/chill.jpg"))
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(GAF(bot))