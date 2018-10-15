import datetime

import discord
from discord.ext import commands
from dinnerplate import BaseCog, SQLiteGuildTable, SQLiteColumn, SQLiteDataType


def time():
    return datetime.datetime.now().strftime("[%b/%d/%Y %H:%M:%S]")


class Logging(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)
        self.guild_storage = SQLiteGuildTable("logging", [SQLiteColumn("log_channel", SQLiteDataType.INTEGER, None)])

    def sanitize(self, member: discord.User) -> str:
        return str(member).replace("@everyone", "@\u200beveryone") \
                .replace("@here", "@\u200bhere") \
                .replace("discord.gg", "invite.hidden")

    @commands.group(invoke_without_command=True)
    async def logging(self, ctx):
        """
        Logs joins, leaves, bans and unbans on a guild to a channel
        """
        channel_id = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.log_channel)
        if channel_id:
            channel = ctx.guild.get_channel(channel_id)
            await ctx.send(f"`Logging for this guild is turned on in channel #{channel}`")
        else:
            await ctx.send("`Logging for this guild is disabled`")

    @logging.command()
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx, channel=None):
        """
        Enables logging
        """
        channel = channel or ctx.channel
        self.bot.database.set(ctx.guild.id, self.guild_storage.columns.log_channel, channel.id)
        await ctx.send(f"`Logging has been enabled in channel #{channel}`")

    @logging.command()
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx):
        """
        Disables logging
        """
        self.bot.database.reset_column(ctx.guild.id, self.guild_storage.columns.log_channel)
        await ctx.send("`Logging has been disabled`")

    async def on_member_join(self, member):
        channel_id = self.bot.database.get(member.guild.id, self.guild_storage.columns.log_channel)
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            await channel.send(f"`{time()}` **{self.sanitize(member)}** joined {member.guild}")

    async def on_member_remove(self, member):
        channel_id = self.bot.database.get(member.guild.id, self.guild_storage.columns.log_channel)
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            await channel.send(f"`{time()}` **{self.sanitize(member)}** left {member.guild}")

    async def on_member_ban(self, guild, member):
        channel_id = self.bot.database.get(guild.id, self.guild_storage.columns.log_channel)
        if channel_id:
            channel = guild.get_channel(channel_id)
            await channel.send(f"`{time()}` **{self.sanitize(member)}** was banned from {guild}")

    async def on_member_unban(self, guild, user):
        channel_id = self.bot.database.get(guild.id, self.guild_storage.columns.log_channel)
        if channel_id:
            channel = guild.get_channel(channel_id)
            await channel.send(f"`{time()}` **{self.sanitize(user)}** was unbanned from {guild}")


setup = Logging.setup
