import asyncio

import discord
from discord.ext import commands
from dinnerplate import BaseCog, SQLiteDataType, SQLiteGuildTable, SQLiteColumn, JsonConfigManager

from utils import net

DEFAULT = {
    "mashape-key": ""
}


class Misc(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)
        self.config = JsonConfigManager("misc.json", DEFAULT)
        self.guild_storage = SQLiteGuildTable("misc", [SQLiteColumn("ts_ban", SQLiteDataType.INTEGER, False)])

    @commands.command()
    @commands.is_owner()
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
    @commands.has_permissions(administrator=True)
    async def teamspeakbansound(self, ctx):
        """
        Toggles playing the teamspeak "User was banned from your channel" sound when a user is banned.
        """
        toggle = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.ts_ban)
        if toggle:
            toggle = False
            await ctx.send("`Disabled Teamspeak ban sound`")
        else:
            toggle = True
            await ctx.send("`Enabled Teamspeak ban sound`")
        self.bot.database.set(ctx.guild.id, self.guild_storage.columns.ts_ban, toggle)

    @commands.command()
    async def gg(self, ctx):
        """
        GG EZ
        """
        await ctx.send(file=discord.File("resources/ggez.jpg"))

    @commands.command()
    async def quote(self, ctx):
        """
        Get's a random famous quote
        """
        _, quote, status = await net.get_url("https://andruxnet-random-famous-quotes.p.mashape.com/?cat=famous&count=1",
                              headers={"X-Mashape-Key": self.config["mashape-key"],
                                       "user-agent": "GAF Bot"})
        if status != 200:
            await ctx.send("Error requesting quote!")
            return
        await ctx.send(f"\"{quote[0]['quote']}\" - *{quote[0]['author']}*")

    async def on_member_ban(self, guild, member):
        if member.voice is None:
            return
        if self.bot.database.get(guild.id, self.guild_storage.columns.ts_ban):
            vc = await member.voice.channel.connect()
            src = discord.FFmpegPCMAudio("resources/user_banned.mp3")
            vc.play(src)
            await asyncio.sleep(5)
            await vc.disconnect()


setup = Misc.setup
