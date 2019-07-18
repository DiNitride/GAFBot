import asyncio
import re

import discord
from discord import Colour
from discord.ext import commands
from dinnerplate import BaseCog, SQLiteDataType, SQLiteColumn, SQLiteGuildTable, SQLiteBool

from utils import reaction_menu

header = "`All Roles on this guild_config which can be assigned.`\n" \
         ":one: `to` :keycap_ten: `can be used to select roles`\n" \
         ":arrow_left: :arrow_right: `to change pages`\n" \
         ":white_check_mark: `to confirm selection,` :x: `to cancel`\n" \
         ":arrows_counterclockwise: `can be used to undo the previous selection`\n" \
         "`You can alternatively use $roles give [role]and $roles take [role]\n" \
         "to add or remove specific roles, however you must type the full role name\n" \
         "which is caps sensitive, the role's ID or mention the role (Although\n" \
         "this might, just might, irritate everyone with this role and get you banned.`"


class CustomRoleConverter(commands.IDConverter):
    """Converts to a :class:`Role`.
    All lookups are via the local guild. If in a DM context, then the lookup
    is done by the global cache.
    The lookup strategy is as follows (in order):
    1. Lookup by ID.
    2. Lookup by mention.
    3. Lookup by name

    Edited to return the input as string if no role is found
    """
    @asyncio.coroutine
    def convert(self, ctx, argument):
        guild = ctx.message.guild
        if not guild:
            raise commands.NoPrivateMessage()

        match = self._get_id_match(argument) or re.match(r'<@&([0-9]+)>$', argument)
        params = dict(id=int(match.group(1))) if match else dict(name=argument)
        result = discord.utils.get(guild.roles, **params)
        if result is None:
            return argument
        return result


class Roles(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)
        self.guild_storage = SQLiteGuildTable("roles", [SQLiteColumn("role_me_lvl", SQLiteDataType.INTEGER, None),
                                                        SQLiteColumn("role_me_roles", SQLiteDataType.JSON, "[]"),
                                                        SQLiteColumn("join_role", SQLiteDataType.INTEGER, None),
                                                        SQLiteColumn("rolestate", SQLiteDataType.BOOL, SQLiteBool.FALSE),
                                                        SQLiteColumn("rolestate_storage", SQLiteDataType.JSON, "{}")])

    @staticmethod
    def get_roles(ids, roles):
        return [role for role in roles if role.id in ids]

    async def setup_role_me(self, ctx):
        role_me_lvl = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.role_me_lvl)
        role_me_roles = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.role_me_roles)

        if len(role_me_roles) == 0:
            await ctx.send("`The role system is disabled for this guild! Add a role to get started`")
            return "disabled", None, None, None

        if role_me_lvl is not None:
            # Level is set
            role = discord.utils.get(ctx.guild.roles, id=role_me_lvl)
            if role > ctx.author.top_role:
                await ctx.send("`You are not a high enough role to access the role system!`")
                return "perms", None, None, None

        roles = Roles.get_roles(role_me_roles, ctx.guild.roles)
        if len(roles) == 0:
            await ctx.send("`No roles available`")
            return "empty", None, None, None

        return "ok", role_me_lvl, role_me_roles, roles

    @commands.group(invoke_without_command=True)
    async def roles(self, ctx):
        """
        Shows roles on the guild that can be assigned
        """
        # Call the universal setup command to pull the roles from the DB
        role_me, role_me_lvl, role_me_roles, roles = await self.setup_role_me(ctx)
        if role_me != "ok":
            return

        # Make a mirror list of the ID list with names for formatting
        names = [role.name for role in roles]

        # Present and collect choices from user
        choices = await reaction_menu.start_reaction_menu(self.bot, names, ctx.author, ctx.channel,
                                                          count=-1, timeout=60, per_page=10, header=header,
                                                          return_from=roles, allow_none=True)

        # None is returned if the user selects no roles or closes the window
        if choices is None:
            return

        author_roles = ctx.author.roles
        added, removed = [], []
        for role in choices:
            if role in author_roles:
                author_roles.remove(role)
                removed.append(role)
            else:
                author_roles.append(role)
                added.append(role)

        await ctx.author.edit(roles=author_roles)
        await ctx.send("```\n"
                       "Roles Added: {}\n"
                       "Roles Removed: {}\n```".format(", ".join([role.name for role in added]),
                                                       ", ".join([role.name for role in removed])))

    @roles.command()
    async def give(self, ctx, *, role: discord.Role):
        """
        The lord give'th
        """
        # Call the universal setup command to pull the roles from the DB
        role_me, role_me_lvl, role_me_roles, roles = await self.setup_role_me(ctx)
        if role_me != "ok":
            return

        author_roles = ctx.author.roles
        if role.id in role_me_roles:
            try:
                author_roles.append(role)
                await ctx.author.edit(roles=author_roles)
                await ctx.send("Added role {}".format(role))
            except discord.HTTPException:
                await ctx.send("Cannot add role! Do you already have it?")

    @roles.command()
    async def take(self, ctx, *, role: discord.Role):
        """
        And the lord take'th
        """
        # Call the universal setup command to pull the roles from the DB
        role_me, role_me_lvl, role_me_roles, roles = await self.setup_role_me(ctx)
        if role_me != "ok":
            return

        author_roles = ctx.author.roles
        if role.id in [r.id for r in author_roles] and role.id in role_me_roles:
            try:
                author_roles.remove(role)
                await ctx.author.edit(roles=author_roles)
                await ctx.send("Removed role {}".format(role))
            except discord.HTTPException:
                await ctx.send("Cannot remove role! Do you have it?")

    @roles.command()
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx, *, role: CustomRoleConverter):
        """
        Adds a role to the list that can be assigned
        """
        # Call the universal setup command to pull the roles from the DB
        role_me, role_me_lvl, role_me_roles, roles = await self.setup_role_me(ctx)
        if role_me == "perms":
            return

        role_me_roles = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.role_me_roles)

        if not isinstance(role, discord.Role):
            await ctx.send("Could not find role! Creating blank role now :crayon: ")
            role = await ctx.guild.create_role(name=role,
                                               colour=Colour.orange(),
                                               mentionable=True,
                                               reason="Role automagically created by GAF Bot for the role list")
        if role.position >= ctx.author.top_role.position:
            await ctx.send("Unable to add role due to Hierarchy")
        else:
            role_me_roles.append(role.id)
            self.bot.database.set(ctx.guild.id, self.guild_storage.columns.role_me_roles, role_me_roles)
            await ctx.send("`Added {} to the role list`".format(role.name))

    @roles.command()
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx, role: discord.Role):
        """
        Removes a role from the list that can be assigned
        """
        # Call the universal setup command to pull the roles from the DB
        role_me, role_me_lvl, role_me_roles, roles = await self.setup_role_me(ctx)
        if role_me != "ok":
            return
        if role.position >= ctx.author.top_role.position:
            await ctx.send("Unable to remove role due to Hierarchy")
        else:
            role_me_roles.remove(role.id)
            self.bot.database.set(ctx.guild.id, self.guild_storage.columns.role_me_roles, role_me_roles)
            await ctx.send("`Removed {} from the role list`".format(role.name))

    @roles.command()
    @commands.has_permissions(manage_roles=True)
    async def reset(self, ctx):
        """
        Warning, completely clears all roles for your guild and turns the role system off!
        """
        self.bot.database.reset_column(ctx.guild.id, self.guild_storage.columns.role_me_lvl)
        self.bot.database.reset_column(ctx.guild.id, self.guild_storage.columns.role_me_roles, raw_json=True)
        await ctx.send("`All roles have been removed from the bots role menu and the system disabled`")

    @roles.command()
    @commands.has_permissions(manage_roles=True)
    async def level(self, ctx, role: discord.Role = None):
        """
        Toggles the role level required for people to use the roles command, pass a role to set, empty to clear
        """
        role_me, role_me_lvl, role_me_roles, roles = await self.setup_role_me(ctx)
        if role_me != "ok":
            return

        if role is None:
            toggle = role
            name = "None"
        else:
            toggle = role.id
            name = role.name

        self.bot.database.set(ctx.guild.id, self.guild_storage.columns.role_me_lvl, toggle)
        await ctx.send(f"`Role level set to {name}`")

    @commands.group(invoke_without_command=True)
    async def joinrole(self, ctx):
        """
        Shows whether the guild has join role assigned
        """
        join_role = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.join_role)
        if join_role is not None:
            role = discord.utils.get(ctx.guild.roles, id=join_role)
        else:
            await ctx.send("`No join role set for the guild`")
            return
        if role is None:
            await ctx.send("Error locating role, please set a new one...")
            await ctx.invoke(self.set)
        else:
            await ctx.send(f"`The join role for this guild is {role.name}`")

    @joinrole.command()
    async def set(self, ctx, role: discord.Role=None):
        """
        Sets and enables the join role for the guild
        """
        if role is None:
            self.bot.database.reset_column(ctx.guild.id, self.guild_storage.columns.join_role)
            await ctx.send(f"`I will not give users any role upon joining the guild`")
        else:
            self.bot.database.set(ctx.guild.id, self.guild_storage.columns.join_role, role.id)
            await ctx.send(f"`I will give new users to the guild the role {role.name}`")

    @commands.group()
    @commands.has_permissions(manage_roles=True)
    async def rolestate(self, ctx):
        """
        Saves users roles when they leave and grants them again when they join
        """
        rs = self.bot.database.get(ctx.guild.id, self.guild_storage.columns.rolestate)
        await ctx.send(f"Rolestate Enabled: {rs}")

    @rolestate.command()
    @commands.has_permissions(manage_roles=True)
    async def enable(self, ctx):
        """
        Enables rolestate
        """
        self.bot.database.set(ctx.guild.id, self.guild_storage.columns.rolestate, True)
        await ctx.send("`Enabled rolestate!`")

    @rolestate.command()
    @commands.has_permissions(manage_roles=True)
    async def disable(self, ctx):
        """
        Disables rolestate
        """
        self.bot.database.set(ctx.guild.id, self.guild_storage.columns.rolestate, False)
        await ctx.send("`Disabled rolestate!`")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        role_me_roles = self.bot.database.get(role.guild.id, self.guild_storage.columns.role_me_roles)
        role_me_lvl = self.bot.database.get(role.guild.id, self.guild_storage.columns.role_me_lvl)
        join_role = self.bot.database.get(role.guild.id, self.guild_storage.columns.join_role)

        # Check if role was in the role system
        if role.id in role_me_roles:
            role_me_roles.remove(role.id)
            self.bot.database.set(role.guild.id, self.guild_storage.columns.role_me_roles, role_me_roles)

        # Check if the join role was the deleted role
        if role.id == join_role:
            self.bot.database.reset_column(role.guild.id, self.guild_storage.columns.join_role)

        # Check if the role was the role system level
        if role.id == role_me_lvl:
            for r in role.guild.roles:
                if r.position == role.position - 1:
                    self.bot.database.set(role.guild.id, self.guild_storage.columns.role_me_lvl, r.id)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        join_role = self.bot.database.get(member.guild.id, self.guild_storage.columns.join_role)
        if join_role is not None:
            role = discord.utils.get(member.guild.roles, id=join_role)
            if role is None:
                self.bot.database.reset_column(member.guild.id, self.guild_storage.columns.join_role)
            else:
                author_roles = member.roles
                author_roles.append(role)
                try:
                    await member.edit(roles=author_roles)
                except discord.HTTPException:
                    pass

        rolestate = self.bot.database.get(member.guild.id, self.guild_storage.columns.rolestate)
        storage = self.bot.database.get(member.guild.id, self.guild_storage.columns.rolestate_storage)
        id = str(member.id)

        if rolestate:
            self.logger.info(f"Rolestate enabled, collecting roles to add for {member}")
            new_roles = []
            nick = None
            try:
                self.logger.debug(f"Loaded stored rolestate data: {storage[id]}")
                for role_id in storage[id]["roles"]:
                    role = discord.utils.get(member.guild.roles, id=role_id)
                    self.logger.debug(f"Searching for role with ID: {role_id}")
                    if role is None:
                        self.logger.debug(f"Error finding role with ID: {role_id}")
                        continue
                    else:
                        if role < discord.utils.get(member.guild.members, id=self.bot.user.id).top_role:
                            self.logger.debug(f"Found role with ID: {role_id}, adding to new role list")
                            new_roles.append(role)
                if storage[id]["nick"]:
                    nick = storage[id]["nick"]
                await member.edit(roles=new_roles, nick=nick)
            except KeyError:
                self.logger.debug(f"Key Error when loading storage for user {member} with ID: {member.id}")
            except discord.HTTPException:
                self.logger.debug(f"Caught HTTP Exception when trying to add roles for rolestate")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        storage = self.bot.database.get(member.guild.id, self.guild_storage.columns.rolestate_storage)
        roles = [role.id for role in member.roles]
        storage[member.id] = {"roles": roles, "nick": member.nick}
        self.logger.debug(f"Saved rolestate for user {member}. Roles: {roles}")
        self.bot.database.set(member.guild.id, self.guild_storage.columns.rolestate_storage, storage)


setup = Roles.setup
