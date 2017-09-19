import json
import asyncio
from datetime import datetime

import discord
from discord.ext import commands
from lxml import etree
import dateparser

from bot.utils import checks, reaction_menu, net

header = "=====================================================\n" \
         "List of all guilds I am in\n" \
         "Click the arrows to move page\n" \
         "====================================================="





class Admin:

    def __init__(self, bot):
        self.bot = bot
        self.statuses = ["Long Live GAF",
                         self.users_and_guilds,
                         self.uptime,
                         self.commands_run,
                         "http://www.neverendinggaf.com"
                         ]
        self.bg_task = self.bot.loop.create_task(self.status_rotator())

    def users_and_guilds(self):
        users = sum(1 for user in self.bot.get_all_members())
        return "{} users in {} guilds".format(users, len(self.bot.guilds))

    def uptime(self):
        currentTime = datetime.now()
        uptime = currentTime - self.bot.start_time
        days = int(uptime.days)
        hours = int(uptime.seconds / 3600)
        minutes = int((uptime.seconds % 3600) / 60)
        seconds = int((uptime.seconds % 3600) % 60)
        return "{}d, {}h, {}m, {}s".format(days, hours, minutes, seconds)

    def commands_run(self):
        return "{} commands ran".format(self.bot.command_count)

    async def status_rotator(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for val in self.statuses:
                if callable(val):
                    val = val()
                await self.bot.change_presence(game=discord.Game(name=val, type=0))
                await asyncio.sleep(180)

    @commands.group(invoke_without_command=True)
    @checks.is_owner()
    async def guilds(self, ctx):
        """
        Lists all of the guilds the bot is in
        """
        guilds = list("{} - ID: {}".format(g.name, g.id) for g in self.bot.guilds)
        await reaction_menu.start_reaction_menu(self.bot, guilds, ctx.author, ctx.channel, count=0,
                                                timeout=60, per_page=60, header=header)

    @guilds.command()
    @checks.is_owner()
    async def leave(self, ctx, guild=None):
        """
        Leaves a specified guild
        """
        guild_names = list("{} - ID: {}".format(g.name, g.id) for g in self.bot.guilds)
        if guild is None:
            guild = await reaction_menu.start_reaction_menu(
                self.bot, guild_names, ctx.author, ctx.channel, count=1,
                timeout=60, per_page=10, header=header, return_from=self.bot.guilds, allow_none=True)
            guild = guild[0]
        else:
            guild = discord.utils.find(lambda s: s.name == guild or str(s.id) == guild, self.bot.guilds)
            if guild is None:
                await ctx.send("Unable to locate guild")
                return
        try:
            await guild.leave()
            await ctx.send("`Successfully left the guild`")
        except discord.HTTPException:
            await ctx.send("`Leaving the guild failed!`")

    @guilds.command()
    @checks.is_owner()
    async def invite(self, ctx, guild=None):
        """
        Creates an invite to a specified server
        """
        guild_names = list("{} - ID: {}".format(g.name, g.id) for g in self.bot.guilds)
        if guild is None:
            guild = await reaction_menu.start_reaction_menu(self.bot, guild_names, ctx.author, ctx.channel, count=1,
                                                            timeout=60, per_page=10, header=header,
                                                            return_from=self.bot.guilds, allow_none=True)
            guild = guild[0]
        else:
            guild = discord.utils.find(lambda s: s.name == guild or str(s.id) == guild, self.bot.guilds)
            if guild is None:
                await ctx.send("`Unable to locate guild`")
                return

        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    invite = await channel.create_invite()
                    await ctx.send("`Created an invite to guild, I will DM it to you`")
                    dm_channel = ctx.author.dm_channel
                    if dm_channel is None:
                        dm_channel = await ctx.author.create_dm()
                    await dm_channel.send(invite.url)
                    break
                except discord.HTTPException:
                    await ctx.send("`Failed to create invite for guild!`")

    @commands.command()
    @checks.is_owner()
    async def clean_bot_guilds(self, ctx):
        for g in self.bot.guilds:
            s = await self.compare_bots_users(g)
            if s == 0:
                await ctx.send(f"Successfully left guild {g} [{g.id}] for having a bot:user ratio too high!")
            elif s == 1:
                await ctx.send(f"Failed leaving guild {g} [{g.id}] for having a bot:user ratio too high!")

    async def on_guild_join(self, guild):
        await self.compare_bots_users(guild)

    async def compare_bots_users(self, guild):
        if guild or guild.id is None:
            return
        b = 0
        u = 0
        for m in guild.members:
            if m.bot:
                b += 1
            else:
                u += 1
        self.bot.logger.debug(f"{guild} [{guild.id}] Evaluated bot to user ratio for guild - Users: {u} Bots: {b}")
        if (b / 2) > u:
            self.bot.logger.debug(f"{guild} [{guild.id}] ratio too high, attempting to leave")
            try:
                await guild.leave()
                self.bot.logger.debug(f"{guild} [{guild.id}] left guild successfully")
                return 0  # left
            except discord.HTTPException:
                self.bot.logger.debug(f"{guild} [{guild.id}] failed leaving guild")
                return 1  # error
        else:
            self.bot.logger.debug(f"{guild} [{guild.id}] Ratio OK, not leaving guild")
            return 2  # nothing


def setup(bot):
    bot.add_cog(Admin(bot))
