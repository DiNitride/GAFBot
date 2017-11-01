import discord
from discord.ext import commands

from bot.utils import checks


class Moderation:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.perms_kick()
    async def kick(self, ctx, user: discord.Member, *, reason: str = None):
        """
        Kicks a user from the guild
        """
        if user.top_role >= ctx.author.top_role:
            return
        await ctx.guild.kick(user,
                             reason=f"Kicked by {ctx.author} for reason \"{reason}\"")
        await ctx.channel.send(f":negative_squared_cross_mark:  Kicked user {user}")
        self.bot.logger.notice("Kicked {} from {}".format(user, ctx.guild.name))

    @commands.command()
    @checks.perms_ban()
    async def ban(self, ctx, user: discord.Member, delete_days=1, *, reason: str = None):
        """
        Bans a user from the guild
        """
        if user.top_role >= ctx.author.top_role:
            return
        if delete_days > 7:
            delete_days = 7
        if user:
            await ctx.guild.ban(user,
                                delete_message_days=delete_days,
                                reason=f"Banned by {ctx.author} for reason \"{reason}\"")
            await ctx.channel.send(f":negative_squared_cross_mark:  Banned user {user}")
            self.bot.logger.notice("Banned {} from {}".format(user, ctx.guild.name))

    @commands.command()
    @checks.perms_ban()
    async def xban(self, ctx, user_id: int):
        """
        Allows the banning of a user not int he guild via ID
        """
        try:
            await ctx.bot.http.ban(user_id, ctx.message.guild.id, 0)
        except discord.Forbidden:
            await ctx.channel.send(":x: 403 FORBIDDEN")
        except discord.NotFound:
            await ctx.channel.send(":x: User not found.")
        else:
            await ctx.channel.send(f":negative_squared_cross_mark:  Banned user {user_id} - <@{user_id}>.")

    @commands.command()
    @checks.perms_manage_messages()
    async def purge(self, ctx, limit: int, user: discord.Member = None):
        """
        Purges messages from a channel
        """
        def predicate(m):
            return m.author == user
        if ctx.message.author.id != 95953002774413312:
            if limit > 100:
                limit = 100
        if user is None:
            messages = await ctx.channel.purge(limit=limit, check=None)
            await ctx.send("Purged {} messages in #{}".format(len(messages), ctx.channel))
            self.bot.logger.notice("Purged {} messages in #{}".format(len(messages), ctx.channel))
        else:
            messages = await ctx.channel.purge(limit=limit, check=predicate)
            await ctx.send("Purged {} messages from {} in #{}".format(len(messages), user, ctx.channel))
            self.bot.logger.notice("Purged {} messages from {} in #{}".format(len(messages), user, ctx.channel))

    @commands.group(invoke_without_command=True)
    @checks.perms_manage_messages()
    async def mute(self, ctx, user: discord.Member):
        """
        Mutes a user
        """
        guild_settings = await self.bot.get_guild_config(ctx.guild.id)
        if guild_settings["mute_role"] == "":
            await ctx.send("No mute role set! Please set one with $mute role <role>")
            return
        mute_role = None
        for role in ctx.guild.roles:
            if role.id == int(guild_settings["mute_role"]):
                mute_role = role
        if mute_role is None:
            return
        if mute_role is None:
            await ctx.send("Invalid mute role")
            return
        if mute_role in user.roles:
            roles = user.roles
            roles.remove(mute_role)
            await user.edit(roles=roles)
            await ctx.send("`{}` -> :100:".format(user))
        else:
            if user.top_role.position >= ctx.author.top_role.position:
                return
            roles = user.roles
            roles.append(mute_role)
            await user.edit(roles=roles)
            await ctx.send("`{}` -> :speak_no_evil:".format(user))

    @mute.command()
    @checks.perms_manage_messages()
    async def role(self, ctx, role: discord.Role):
        """
        Sets the mute role for the server
        """
        if role >= ctx.author.top_role:
            await ctx.send("Unable to add role due to Hierarchy")
        else:
            guild_config = await self.bot.get_guild_config(ctx.guild.id)
            guild_config["mute_role"] = role.id
            await self.bot.set_guild_config(ctx.guild.id, guild_config)
            await ctx.send("Set the guilds mute role")

    async def on_guild_role_delete(self, role):
        guild_config = await self.bot.get_guild_config(role.guild.id)
        mute_role = guild_config["mute_role"]
        if mute_role == role.id:
            guild_config["mute_role"] = ""
            await self.bot.set_guild_config(role.guild.id, guild_config)


def setup(bot):
    bot.add_cog(Moderation(bot))
