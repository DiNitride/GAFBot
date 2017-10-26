import asyncio

from discord.ext import commands
import discord
import dateparser
import html2text
from lxml import etree

from bot.utils import checks, net


class GAF:

    def __init__(self, bot):
        self.bot = bot
        # self.bg_task = self.bot.loop.create_task(self.gaf_update_loop())

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
    @checks.is_gaf_server()
    async def chill(self, ctx):
        """
        Channel 1 and chill?
        """
        await ctx.send(content="<@&172426880543227904> <@&262334316611239937>, chill? - {}".format(ctx.author), file=discord.File("bot/resources/chill.jpg"))
        await ctx.message.delete()

    @gaf.group(invoke_without_subcommand=True)
    @checks.perms_manage_messages()
    async def rss(self, ctx):
        """
        Allows you to manage RSS feed for GAF Steam Annoucements. BROKEN
        """
        pass

    @rss.command()
    async def track(self, ctx):
        """
        Enables tracking GAF RSS updates for your guild.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["gaf_steam_rss"] = True
        guild_config["gaf_steam_rss_channel"] = ctx.channel.id
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, tracking GAF RSS updates in channel #{}`".format(ctx.channel))

    @rss.command()
    async def stop(self, ctx):
        """
        Disables tracking GAF RSS updates on your guild.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["gaf_steam_rss"] = False
        guild_config["gaf_steam_rss_channel"] = ""
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, no longer tracking GAF RSS updates`")

    @rss.command()
    async def set(self, ctx):
        """
        Set's the channel in which the updates will be posted.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["gaf_steam_rss_channel"] = ctx.channel.id
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, tracking channel set to #{}`".format(ctx.channel))



def setup(bot):
    bot.add_cog(GAF(bot))