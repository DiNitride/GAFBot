from discord.ext import commands
import discord

from bot.utils import checks


class Misc:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.perms_manage_nicks()
    async def massnick(self, ctx, prefix, overwrite, suffix):
        """
        Mass nicknames everyone on the server, please do $help massnick
        Prefix: The prefix to apply to their name
        Overwrite: Option to overwrite everyones name
        Suffix: The suffix to apply to their name
        Items must be included in quotes, and also must be specified by name.
        Examples:
            $massnick "Merry " "" " Christmas"
            $massnick "" "Vizual" ""
        """
        success = 0
        error = 0
        forbidden = 0
        for m in ctx.guild.members:
            try:
                await m.edit(
                    reason=f"Massnick command used by {ctx.author}",
                    nick=f"{prefix}{overwrite or m.name}{suffix}"
                )
                success += 1
            except discord.errors.Forbidden:
                forbidden += 1
            except discord.errors.HTTPException:
                error += 1
        await ctx.send("Complete massnick operation!\n"
                       f"Updated `{success}` nickanmes\n"
                       f"Failed to update `{error + forbidden}`\n"
                       f"Missing permissions for `{forbidden}`\n"
                       f"Other exception for `{error}`")


def setup(bot):
    bot.add_cog(Misc(bot))