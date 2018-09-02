from dinnerplate import BaseCog
import discord
from discord.ext import commands

from utils import checks


class GAF(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)

    @commands.group(invoke_without_command=True)
    async def gaf(self, ctx):
        """
        Information on The Never Ending GAF
        """
        await ctx.send("The Never Ending GAF is a small group of idiots that play games and insult each other. "
                       "\nWe reside on our Discord server, usually in the beloved cesspool intelligently "
                       "titled \"Channel 1\".\nFeel free to pop by, probably get told to piss off, and maybe "
                       "play some games."
                       "\nMore info and invite links: <http://www.neverendinggaf.com>")

    @gaf.command()
    async def website(self, ctx):
        """
        Link to The Never Ending GAF's Website
        """
        await ctx.send("<http://www.neverendinggaf.com>")

    @gaf.command()
    async def invite(self, ctx):
        """
        GAF Guild Invite
        """
        await ctx.send("<http://discord.neverendinggaf.com>")

    @commands.command()
    async def neogaf(self, ctx):
        """
        IS THIS NEOGAF????
        """
        resp = "`Is this NeoGAF?`\n" \
               "~~NO WHY THE FUCK DO YOU ALL KEEP JOINING AND ASKING IF THIS IS NEOGAF?~~\n" \
               "No, we're not NeoGAF, we're The Never Ending GAF, a European gaming community. " \
               "We play games and insult each other a lot, so while we aren't what you're looking for, feel free to " \
               "stick around and join us playing games and shit. You can read more about what we do on our website at " \
               "<http://www.neverendinggaf.com> or in #welcome-to-gaf\n"
        await ctx.send(resp)

    @commands.command()
    @checks.is_gaf_server()
    async def chill(self, ctx):
        """
        Channel 1 and chill?
        """
        await ctx.send(
            content=f"<@&172426880543227904> <@&262334316611239937>, I am lonely and want attention - {ctx.author}",
            file=discord.File("resources/thank_you_all_for_coming.jpg"))
        await ctx.message.delete()


setup = GAF.setup
