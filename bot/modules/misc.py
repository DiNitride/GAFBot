from discord.ext import commands
import discord

from bot.utils import checks


class Misc:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_owner()
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

    @commands.command()
    async def f(self, ctx):
        """
        Pays respects
        """
        await ctx.send("*Pays respects*")

    @commands.command()
    async def teamspeakbansound(self, ctx):
        """
        Toggles playing the teamspeak "User was banned from your channel" sound when a user is banned.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        if guild_config["teamspeakBanSound"]:
            guild_config["teamspeakBanSound"] = False
            await ctx.send("`Disabled Teamspeak ban sound`")
        else:
            guild_config["teamspeakBanSound"] = True
            await ctx.send("`Enabled Teamspeak ban sound`")
        await self.bot.set_guild_config(ctx.guild.id, guild_config)

    async def on_member_ban(self, guild, member):
        if member.voice.channel is None:
            return
        guild_config = await self.bot.get_guild_config(guild.id)
        if guild_config["teamspeakBanSound"]:
            vc = await member.voice.channel.connect()
            src = discord.FFmpegPCMAudio("bot/resources/user_banned.mp3")
            vc.play(src)
            while True:
                if not vc.is_playing():
                    await vc.disconnect()


def setup(bot):
    bot.add_cog(Misc(bot))