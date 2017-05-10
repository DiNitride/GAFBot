import discord
from discord.ext import commands
from utils import checks


class Moderation:

    def __init__(self, bot):
        self.bot = bot
        self.ban.enabled = bot.modules["moderation"]
        self.kick.enabled = bot.modules["moderation"]
        self.xban.enabled = bot.modules["moderation"]
        self.purge.enabled = bot.modules["moderation"]

    @commands.command()
    @checks.perms_ban()
    async def ban(self, ctx, user: discord.Member, delete_days=1):
        """Bans a user from the guild"""
        self.bot.cmd_log(ctx, "ban")
        if delete_days > 7:
            delete_days = 7
        if user:
            await ctx.guild.ban(user, delete_message_days=delete_days)
            self.bot.log.notice("Kicked {} from {}".format(user, ctx.guild.name))

    @commands.command()
    @checks.perms_ban()
    async def xban(self, ctx, user_id: int):
        """Allows the banning of a user not int he guild via ID"""
        # Stolen from Joku
        # k thnx Laura
        # https://github.com/SunDwarf/Jokusoramame/blob/master/joku/cogs/mod.py#L135
        try:
            await ctx.bot.http.ban(user_id, ctx.message.guild.id, 0)
        except discord.Forbidden:
            await ctx.channel.send(":x: 403 FORBIDDEN")
        except discord.NotFound:
            await ctx.channel.send(":x: User not found.")
        else:
            await ctx.channel.send(":negative_squared_cross_mark:  Banned user {}.".format(user_id))

        self.bot.cmd_log(ctx, "xban")

    @commands.command()
    @checks.perms_kick()
    async def kick(self, ctx, user: discord.Member):
        """Kicks a user from the guild"""
        self.bot.cmd_log(ctx, "kick")
        if user:
            await ctx.guild.kick(user)
            self.bot.log.notice("Kicked {} from {}".format(user, ctx.guild.name))

    @commands.command()
    @checks.perms_manage_messages()
    async def purge(self, ctx, limit: int, user: discord.Member = None):
        """Purges messages from a channel"""
        def predicate(m):
            return m.author == user
        if ctx.message.author.id != 95953002774413312:
            if limit > 100:
                limit = 100
        if user is None:
            messages = await ctx.channel.purge(limit=limit, check=None)
            await ctx.send("Purged {} messages in #{}".format(len(messages), ctx.channel))
            self.bot.log.notice("Purged {} messages in #{}".format(len(messages), ctx.channel))
        else:
            messages = await ctx.channel.purge(limit=limit, check=predicate)
            await ctx.send("Purged {} messages from {} in #{}".format(len(messages), user, ctx.channel))
            self.bot.log.notice("Purged {} messages from {} in #{}".format(len(messages), user, ctx.channel))
        self.bot.cmd_log(ctx, "Purged messages")


def setup(bot):
    bot.add_cog(Moderation(bot))
