import discord
from discord.ext import commands
from utils import checks
import datetime


def time():
    return datetime.datetime.now().strftime("[%b/%d/%Y %H:%M:%S]")


class Config:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        """Show's prefix"""
        server = await self.bot.get_server_data(ctx.guild.id)
        await ctx.send("The prefix for the bot on this server is: `{}`\n"
                       "You can set a new one with `{}prefix set 'new_prefix'`".format(server["prefix"], server["prefix"]))
        self.bot.cmd_log(ctx, "Prefix check")

    @prefix.command()
    @checks.perms_manage_guild()
    async def set(self, ctx, *, new_prefix: str):
        """Updates the bot's prefix"""
        server = await self.bot.get_server_data(ctx.guild.id)
        server["prefix"] = new_prefix
        await self.bot.update_prefix_cache(ctx.guild.id, new_prefix)
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("Updated bot prefix to: {}".format(server["prefix"]))
        self.bot.cmd_log(ctx, "Prefix updated to {}".format(new_prefix))

    @commands.group(invoke_without_command=True)
    async def logging(self, ctx):
        """Shows status of server logging"""
        server = await self.bot.get_server_data(ctx.guild.id)
        if server["loggingOn"] is False:
            await ctx.send("`Logging for this server is turned off`")
        else:
            print(server["loggingChannel"])
            channel = ctx.guild.get_channel(int(server["loggingChannel"]))
            await ctx.send("`Logging for this server is turned on in channel #{}`".format(channel))
        self.bot.cmd_log(ctx, "Logging check")

    @logging.command()
    @checks.perms_manage_guild()
    async def enable(self, ctx):
        server = await self.bot.get_server_data(ctx.guild.id)
        if server["loggingChannel"] == "":
            channel = ctx.channel.id
        server["loggingOn"] = True
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Logging has been enabled`")
        self.bot.cmd_log(ctx, "Server logging enabled")

    @logging.command()
    @checks.perms_manage_guild()
    async def disable(self, ctx):
        server = await self.bot.get_server_data(ctx.guild.id)
        server["loggingOn"] = False
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Logging has been disabled`")
        self.bot.cmd_log(ctx, "Server logging disabled")

    @logging.command()
    @checks.perms_manage_guild()
    async def set(self, ctx):
        server = await self.bot.get_server_data(ctx.guild.id)
        server["loggingChannel"] = ctx.channel.id
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Logging channel has been set to #{}`".format(ctx.channel))

    async def on_member_join(self, member):
        server = await self.bot.get_server_data(member.guild.id)
        if server["loggingOn"] is True:
            channel = member.guild.get_channel(server["loggingChannel"])
            await channel.send("`{}` **{}** joined {}".format(time(), member, member.guild))

    async def on_member_remove(self, member):
        server = await self.bot.get_server_data(member.guild.id)
        if server["loggingOn"] is True:
            channel = member.guild.get_channel(server["loggingChannel"])
            await channel.send("`{}` **{}** left {}".format(time(), member, member.guild))

    async def on_member_ban(self, member):
        server = await self.bot.get_server_data(member.guild.id)
        if server["loggingOn"] is True:
            channel = member.guild.get_channel(server["loggingChannel"])
            await channel.send("`{}` **{}** was banned from {}".format(time(), member, member.guild))

    async def on_member_unban(self, guild, user):
        server = await self.bot.get_server_data(guild.id)
        if server["loggingOn"] is True:
            channel = guild.get_channel(server["loggingChannel"])
            await channel.send("`{}` **{}** was unbanned from {}".format(time(), user, guild))


def setup(bot):
    bot.add_cog(Config(bot))
