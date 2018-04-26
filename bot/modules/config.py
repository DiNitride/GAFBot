import datetime

from discord.ext import commands

from bot.utils import checks


def time():
    return datetime.datetime.now().strftime("[%b/%d/%Y %H:%M:%S]")


class Config:
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def prefix(self, ctx):
        """
        Show's prefix for guild.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        await ctx.send(f"The prefix for the bot on this guild is: `{guild_config['prefix']}`\n"
                       f"You can set a new one with `{guild_config['prefix']}prefix set 'new_prefix'`")

    @prefix.command(name="set")
    @checks.perms_manage_guild()
    async def _set(self, ctx, *, new_prefix: str = None):
        """
        Updates the bot's prefix.
        """
        if new_prefix is None:
            return
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["prefix"] = new_prefix
        self.bot.prefix_cache[ctx.guild.id] = new_prefix
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send(f"Updated bot prefix to: {new_prefix}")

    @commands.group(invoke_without_command=True)
    async def logging(self, ctx):
        """
        Shows status of guild logging.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        if guild_config["loggingOn"] is False:
            await ctx.send("`Logging for this guild is turned off`")
        else:
            channel = ctx.guild.get_channel(int(guild_config["loggingChannel"]))
            await ctx.send(f"`Logging for this guild is turned on in channel #{channel}`")

    @logging.command()
    @checks.perms_manage_guild()
    async def enable(self, ctx):
        """
        Enables logging
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        if guild_config["loggingChannel"] == "":
            guild_config["loggingChannel"] = ctx.channel.id
        guild_config["loggingOn"] = True
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Logging has been enabled`")

    @logging.command()
    @checks.perms_manage_guild()
    async def disable(self, ctx):
        """
        Disables logging
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["loggingOn"] = False
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Logging has been disabled`")

    @logging.command()
    @checks.perms_manage_guild()
    async def set(self, ctx):
        """
        Set's the logging channel
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["loggingChannel"] = ctx.channel.id
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Logging channel has been set to #{}`".format(ctx.channel))

    @commands.command(name="enable")
    @checks.perms_manage_guild()
    async def _enable(self, ctx, module_name: str = None):
        """
        Enables a module for the guild
        """
        module_name = module_name.lower()
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        if module_name == "config" or module_name == "core":
            await ctx.send("This cog is always enabled")
            return
        if module_name in guild_config["modules"].keys():
            guild_config["modules"][module_name] = True
            await ctx.send(f"Enabled module {module_name} for this guild")
            await self.bot.set_guild_config(ctx.guild.id, guild_config)
        else:
            await ctx.send("`Invalid module`")

    @commands.command(name="disable")
    @checks.perms_manage_guild()
    async def _disable(self, ctx, module_name: str = None):
        """
        Disables a module for the guild
        """
        module_name = module_name.lower()
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        if module_name == "config" or module_name == "core":
            await ctx.send("This cog is always enabled")
            return
        if module_name in guild_config["modules"].keys():
            guild_config["modules"][module_name] = False
            await ctx.send(f"Disabled module {module_name} for this guild")
            await self.bot.set_guild_config(ctx.guild.id, guild_config)

    @commands.command()
    @checks.perms_manage_guild()
    async def clear(self, ctx):
        """WARNING: Clears the config for the guild"""
        guild_config = self.bot.default_guild_config
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`:warning: Config cleared`")

    async def on_member_join(self, member):
        guild_config = await self.bot.get_guild_config(member.guild.id)
        if guild_config["loggingOn"] is True:
            channel = member.guild.get_channel(guild_config["loggingChannel"])
            await channel.send("`{}` **{}** joined {}".format(time(), member, member.guild))

    async def on_member_remove(self, member):
        guild_config = await self.bot.get_guild_config(member.guild.id)
        if guild_config["loggingOn"] is True:
            channel = member.guild.get_channel(guild_config["loggingChannel"])
            await channel.send("`{}` **{}** left {}".format(time(), member, member.guild))

    async def on_member_ban(self, guild, member):
        guild_config = await self.bot.get_guild_config(guild.id)
        if guild_config["loggingOn"] is True:
            channel = guild.get_channel(guild_config["loggingChannel"])
            await channel.send("`{}` **{}** was banned from {}".format(time(), member, guild))

    async def on_member_unban(self, guild, user):
        guild_config = await self.bot.get_guild_config(guild.id)
        if guild_config["loggingOn"] is True:
            channel = guild.get_channel(guild_config["loggingChannel"])
            await channel.send("`{}` **{}** was unbanned from {}".format(time(), user, guild))


def setup(bot):
    bot.add_cog(Config(bot))
