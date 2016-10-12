import discord
from discord.ext import commands
from utils import checks

class Moderation():
    def __init__(self, bot):
        self.bot = bot

    # Banning and Kicking commands

    # Bans a member
    @commands.command()
    @commands.check(checks.perm_ban)
    async def ban(self, member: discord.Member = None):
        """Bans a member
        Usage:
        $ban @recchan
        User and bot must both have ban member permissions"""
        # Are they trying to ban nobody? Are they stupid?
        # Why do they have mod powers if they're this much of an idiot?
        if member is None:
            return
        # Is the person being banned me? No we don't allow that
        elif member.id == '95953002774413312':
            await self.bot.say("http://i.imgur.com/BSbBniw.png")
            return
        # Bans the user
        await self.bot.ban(member, delete_message_days=1)
        # Prints to console

    # Kicks a member
    @commands.command()
    @commands.check(checks.perm_kick)
    async def kick(self, member: discord.Member = None):
        """Kicks a member
        Usage:
        $kick @recchan
        User and bot must both have kick member permissions"""
        # Same as above, are they stupid
        if member is None:
            return
        # Still not allowed to kick me
        elif member.id == '95953002774413312':
            await self.bot.say("http://i.imgur.com/BSbBniw.png")
            return
        # Kicks the user
        await self.bot.kick(member)
        # Prints to console

    # Information commands
    # Server info and member info

    # Gives the user some basic info on a user
    @commands.command(pass_context=True)
    async def info(self, ctx, member : discord.Member = None):
        """Infomation on a user
        Usage:
        $info @DiNitride
        If no member is specified, it defaults to the sender"""
        if member == None:
            member = ctx.message.author
        await self.bot.say(
            "```xl\n" +
            "Name: {0.name}\n".format(member) +
            "Joined server: {0.joined_at}\n".format(member) +
            "ID: {0.id}\n".format(member) +
            "Has existed since: {0.created_at}\n".format(member) +
            "Bot?: {0.bot}\n".format(member) +
            "```" +
            "\n{0.avatar_url}".format(member))

    # Server Info
    @commands.command(pass_context=True)
    async def serverinfo(self, ctx):
        """Shows server information
        Usage:
        $serverinfo"""
        server = ctx.message.server
        afk = server.afk_timeout / 60
        await self.bot.say(
            "```xl\n" +
            "Name: {0.name}\n".format(server) +
            "Server ID: {0.id}\n".format(server) +
            "Region: {0.region}\n".format(server) +
            "Existed since: {0.created_at}\n".format(server) +
            "Owner: {0.owner}\n".format(server) +
            "AFK Timeout and Channel: {0} minutes in '{1.afk_channel}'\n".format(afk, server) +
            "Member Count: {0.member_count}\n".format(server) +
            "```")

    @commands.command(pass_context=True)
    @commands.check(checks.perm_manage_messages)
    async def purge(self, ctx, amount: int = None, user: discord.User = None):
        """Removes a specified amount of messages, either from a specific user or all.
        Usage:
        $purge 100 @User
        Limit: 150
        User and bot must both have manage messages permissions"""
        channel = ctx.message.channel

        if amount is None:
            amount = 100

        if ctx.message.author.id != self.bot.config["ids"]["owner"]:
            if amount > 150:
                amount = 150

        def check_user(m):
            return m.author == user

        if user is None:
            purged = await self.bot.purge_from(channel, limit=amount, check=None)
        else:
            purged = await self.bot.purge_from(channel, limit=amount, check=check_user)

        if user is None:
            output = "Removed {0} messages".format(len(purged))
        else:
            output = "Removed {0} messages by {1.name}".format(len(purged), user)

        await self.bot.say(output)



def setup(bot):
    bot.add_cog(Moderation(bot))
