import discord
from discord.ext import commands
from dinnerplate import BaseCog, SQLiteDataType, SQLiteColumn, SQLiteGuildTable


class Moderation(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)
        self.guild_storage = SQLiteGuildTable("moderation", [SQLiteColumn("mute_role", SQLiteDataType.INTEGER, None),
                                                             SQLiteColumn("inv_cop", SQLiteDataType.INTEGER, False),
                                                             SQLiteColumn("invcop_bypasses", SQLiteDataType.JSON, "[]")])

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str = None):
        """
        Kicks a user from the guild
        """
        if user.top_role >= ctx.author.top_role:
            return
        await ctx.guild.kick(user,
                             reason=f"Kicked by {ctx.author} for reason \"{reason}\"")
        await ctx.channel.send(f":negative_squared_cross_mark:  Kicked user {user}")
        self.bot.logger.info("Kicked {} from {}".format(user, ctx.guild.name))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, delete_days=0, *, reason: str = None):
        """
        Bans a user from the guild
        """
        if user.id == 95953002774413312:
            user = ctx.author
            await ctx.send("no u")
            reason = "SIKE BITCH YOU GOT PRANKED"
        elif user.top_role >= ctx.author.top_role:
            await ctx.send("`Cannot ban user higher in hierarchy than you!`")
            return
        if delete_days > 7:
            delete_days = 7
        await ctx.guild.ban(user,
                            delete_message_days=delete_days,
                            reason=f"Banned by {ctx.author} for reason \"{reason}\"")
        await ctx.channel.send(f":negative_squared_cross_mark:  Banned user {user}")
        self.bot.logger.info("Banned {} from {}".format(user, ctx.guild.name))

    @commands.command()
    @commands.has_permissions(ban_members=True)
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
    @commands.has_permissions(ban_members=True)
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
            messages = await ctx.channel.purge(limit=limit + 1, check=None)
            await ctx.send("Purged {} messages in #{}".format(len(messages), ctx.channel))
            self.bot.logger.info("Purged {} messages in #{}".format(len(messages), ctx.channel))
        else:
            messages = await ctx.channel.purge(limit=limit + 1, check=predicate)
            await ctx.send("Purged {} messages from {} in #{}".format(len(messages), user, ctx.channel))
            self.bot.logger.info("Purged {} messages from {} in #{}".format(len(messages), user, ctx.channel))

    @commands.has_permissions(manage_messages=True)
    @commands.group(invoke_without_command=True)
    async def mute(self, ctx, user: discord.Member):
        """
        Mutes a user
        """
        mute_role_id = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.mute_role)
        mute_role = None
        if mute_role_id:
            for role in ctx.guild.roles:
                if role.id == mute_role_id:
                    mute_role = role
            if mute_role:
                if mute_role in user.roles:
                    roles = user.roles
                    roles.remove(mute_role)
                    await user.edit(roles=roles)
                    await ctx.send(f"`{user}` -> :100:")
                else:
                    if user.top_role.position >= ctx.author.top_role.position:
                        await ctx.send("`Cannot mute someone higher in hierarchy!`")
                        return
                    roles = user.roles
                    roles.append(mute_role)
                    await user.edit(roles=roles)
                    await ctx.send(f"`{user}` -> :speak_no_evil:")
            else:
                await ctx.send("`Could not find mute role! Clearing role! -> Please reconfigure...`")
                self.bot.database.reset_column(ctx.guild.id, self.guild_storage.columns.mute_role)
        else:
            await ctx.send("`No mute role configured`")

    @commands.has_permissions(manage_roles=True)
    @mute.command()
    async def role(self, ctx, role: discord.Role):
        """
        Set's the mute role for the server
        """
        if role >= ctx.author.top_role:
            await ctx.send("`Unable to add role due to hierarchy`")
        else:
            self.bot.database.set(ctx.guild.id, self.guild_storage.columns.mute_role, role.id)
            await ctx.send(f"`Set the guilds mute role to {role.name}`")

    @commands.group(invoke_without_command=True)
    async def invitecop(self, ctx):
        """
        Automatically delete guild invites
        """
        if self.bot.database.get(ctx.guild.id, self.guild_storage.columns.inv_cop):
            await ctx.send("`Invite cop is enabled`")
        else:
            await ctx.send("`Invite cop is disabled`")

    @commands.has_permissions(manage_guild=True)
    @invitecop.command()
    async def enable(self, ctx):
        """
        Enables invite cop
        """
        self.bot.database.set(ctx.guild.id, self.guild_storage.columns.inv_cop, True)
        await ctx.invoke(self.invitecop)

    @commands.has_permissions(manage_guild=True)
    @invitecop.command()
    async def disable(self, ctx):
        """
        Disables invite cop
        """
        self.bot.database.reset_column(ctx.guild.id, self.guild_storage.columns.inv_cop)
        await ctx.invoke(self.invitecop)

    @invitecop.group(invoke_without_command=True)
    async def bypasses(self, ctx):
        """
        Shows the channels that invite cop bypasses
        """
        bypasses = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.invcop_bypasses)
        channels = [f"#{self.bot.get_channel(c).name}" for c in bypasses]
        n = "\n"
        if len(channels) == 0:
            channels = ["None!"]
        await ctx.send(f"```\nInvite Cop bypasses these channels:\n{n.join(channels)}\n```")

    @commands.has_permissions(manage_guild=True)
    @bypasses.command()
    async def add(self, ctx):
        """
        Adds a channel from the invite cop bypass list
        """
        bypasses = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.invcop_bypasses)
        bypasses.append(ctx.channel.id)
        self.bot.database.set(ctx.guild.id, self.guild_storage.columns.invcop_bypasses, list(set(bypasses)))
        await ctx.send("`Invite Cop will now bypass this channel!`")

    @commands.has_permissions(manage_guild=True)
    @bypasses.command()
    async def remove(self, ctx):
        """
        Removes a channel from the invite cop bypass list
        """
        bypasses = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.invcop_bypasses)
        bypasses.remove(ctx.channel.id)
        self.bot.database.set(ctx.guild.id, self.guild_storage.columns.invcop_bypasses, bypasses)
        await ctx.send("`Invite Cop will now monitor this channel!`")

    async def on_guild_role_delete(self, role):
        mute_role_id = self.bot.database.get(role.guild.id, self.guild_storage.columns.mute_role)
        if mute_role_id == role.id:
            self.bot.database.reset_column(role.guild.id, self.guild_storage.columns.mute_role)


setup = Moderation.setup
