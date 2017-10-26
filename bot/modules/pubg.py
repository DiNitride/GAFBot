import asyncio

import discord
from discord.ext import commands
import dateparser
from lxml import etree
import html2text

from bot.utils import net, checks


class PUBG:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(disabled = True)
    @checks.perms_manage_messages()
    async def pubgupdates(self, ctx):
        """
        Manages tracking PUBG updates for your guild.
        """
        pass

    @pubgupdates.command()
    async def track(self, ctx):
        """
        Enables tracking PUBG updates for your guild.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["pubg_updates"] = True
        guild_config["pubg_updates_channel"] = ctx.channel.id
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, tracking PUBG updates in channel #{}`".format(ctx.channel))

    @pubgupdates.command()
    async def stop(self, ctx):
        """
        Disables tracking PUBG updates on your guild.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["pubg_updates"] = False
        guild_config["pubg_updates_channel"] = ""
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, no longer tracking PUBG updates`")

    @pubgupdates.command()
    async def set(self, ctx):
        """
        Set's the channel in which the updates will be posted.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["pubg_updates_channel"] = ctx.channel.id
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, tracking channel set to #{}`".format(ctx.channel))


def setup(bot):
    bot.add_cog(PUBG(bot))
