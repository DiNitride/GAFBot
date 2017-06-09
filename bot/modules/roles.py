import asyncio

import discord
from discord.ext import commands

from utils import reaction_menu
from utils import checks

header = "=====================================================\n" \
         "All Roles on this server which can be assigned.\n" \
         ":one: to :keycap_ten: can be used to select roles\n" \
         ":arrow_left: :arrow_right: to change pages\n" \
         ":white_check_mark: to confirm selection, :x: to cancel\n" \
         ":arrows_counterclockwise: can be used to undo the previoux selection\n" \
         "====================================================="


class Roles:


    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def roles(self, ctx):
        """Shows roles on the server that can be assigned"""
        server = await self.bot.get_server_data(ctx.guild.id)
        options = server["roles"]
        if len(options) == 0:
            await ctx.send("No roles available")
            return
        choices = await reaction_menu.start_reaction_menu(self.bot, list(options.values()), ctx.author, ctx.channel, count=-1, timeout=60, per_page=10, header=header, return_from=list(options), allow_none=True)
        if choices is None:
            return
        roles = ctx.author.roles
        r_add = ""
        r_remove = ""
        for role in ctx.guild.roles:
            if str(role.id) in choices and role not in ctx.author.roles:
                roles.append(role)
                r_add += "{}, ".format(role.name)
            elif str(role.id) in choices and role in ctx.author.roles:
                roles.remove(role)
                r_remove += "{}, ".format(role.name)
        if r_add != "":
            r_add = r_add[:-2]
        else:
            r_add = "None"
        if r_remove != "":
            r_remove = r_remove[:-2]
        else:
            r_remove = "None"
        await ctx.author.edit(roles=roles)
        msg = await ctx.send("```\nRoles Added: {}\nRoles Removed: {}\n```".format(r_add, r_remove))
        await asyncio.sleep(20)
        await msg.delete()

    @roles.command()
    @checks.perms_manage_roles()
    async def add(self, ctx, role: discord.Role = None):
        """Adds a role to the list that can be assigned"""
        if role is None:
            return
        if role.position >= ctx.author.top_role.position:
            await ctx.send("Unable to add role due to Hierarchy")
        else:
            server = await self.bot.get_server_data(ctx.guild.id)
            server["roles"][role.id] = role.name
            await self.bot.update_server_data(ctx.guild.id, server)
            await ctx.send("Added {} to the role list".format(role.name))

    @roles.command()
    @checks.perms_manage_roles()
    async def remove(self, ctx, role: discord.Role = None):
        """Removes a role from the list that can be assigned"""
        if role is None:
            return
        if role.position >= ctx.author.top_role.position:
            await ctx.send("Unable to remove role due to Hierarchy")
        else:
            server = await self.bot.get_server_data(ctx.guild.id)
            del server["roles"][str(role.id)]
            await self.bot.update_server_data(ctx.guild.id, server)
            await ctx.send("Removed {} from the role list".format(role.name))

    @roles.command()
    async def reset(self, ctx):
        """Warning, completely ereases config for your server!"""
        guild_data = await self.bot.get_server_data(ctx.guild.id)
        guild_data["roles"] = {}
        await self.bot.update_server_data(ctx.guild.id, guild_data)
        await ctx.send("`All roles have been removed from the bots role menu")

    async def on_guild_role_delete(self, role):
        guild = role.guild
        guild_data = await self.bot.get_server_data(guild.id)
        roles = guild_data["roles"]
        r_id = str(role.id)
        if r_id in roles:
            del guild_data["roles"][r_id]
        await self.bot.update_server_data(guild.id, guild_data)


def setup(bot):
    bot.add_cog(Roles(bot))
