import asyncio
import subprocess

import discord
from discord.ext import commands
from dinnerplate import BaseCog, JsonConfigManager

from utils import reaction_menu
from utils.errors import UserBlacklisted

CONFIG = {
    "blacklist": [],
    "additional_statuses": []
}


class Admin(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)
        self.statuses = ["Long Live GAF",
                         "http://www.neverendinggaf.com",
                         self.sum_users_and_guilds,
                         self.uptime,
                         self.commands_run
                         ]
        self.bot.add_check(self.user_in_blacklist_check)
        self.config = JsonConfigManager("admin.json", default=CONFIG)
        self.statuses.extend(self.config["additional_statuses"])
        self.bg_task = self.bot.loop.create_task(self.status_rotator())

    def sum_users_and_guilds(self):
        _, guilds, _, users,  = self.bot.stats
        return "{} users in {} guilds".format(users, guilds)

    def uptime(self):
        time = self.bot.uptime
        return "{}d, {}h, {}m, {}s".format(time[1][3], time[1][2], time[1][1], time[1][0])

    def commands_run(self):
        return "{} commands ran".format(self.bot._command_count)


    async def status_rotator(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            print("Starting status loop")
            for val in self.statuses:
                print("Iterate next status")
                if callable(val):
                    val = val()
                    print("Called callable status")
                await self.bot.change_presence(activity=discord.Game(name=val))
                print(f"Changed status to {val}")
                await asyncio.sleep(1)
                print("Finished sleeping")

    @commands.group(invoke_without_command=True)
    @commands.is_owner()
    async def guilds(self, ctx):
        """
        Lists all of the guilds the bot is in
        """
        guilds = [g.name for g in self.bot.guilds]
        await reaction_menu.start_reaction_menu(self.bot, guilds, ctx.author, ctx.channel, count=0,
                                                timeout=60, per_page=20, header="name jeff")

    @guilds.command()
    @commands.is_owner()
    async def leave(self, ctx, *, guild):
        """
        Leaves a specified guild
        """
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
    @commands.is_owner()
    async def invite(self, ctx, *, guild):
        """
        Creates an invite to a specified server
        """
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

    @commands.is_owner()
    @guilds.command()
    async def top(self, ctx):
        """
        Get's the top 25 guilds with most members
        """
        ordered = sorted(self.bot.guilds, key=lambda g: len(g.members), reverse=True)[:25]
        embed = discord.Embed(title="Top 25 Guilds Ordered by Member Count", colour=discord.Colour.gold())

        for guild in ordered:
            embed.add_field(name=guild.name, value=f"Count: {len(guild.members)}\nID: {guild.id}", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def update_avatar(self, ctx, file=None):
        file = file or "avatar.jpg"
        try:
            with open(f"resources/{file}", "rb") as f:
                await self.bot.user.edit(avatar=f.read())
            await ctx.send("Updated avatar, am I pretty yet?")
        except FileNotFoundError:
            await ctx.send(f"Couldn't find `resources/{file}`")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def purge_bot_guilds(self, ctx):
        """
        Purges guilds with a bot:user ratio higher than 2:1
        """
        passed = 0
        failed = 0
        success = 0
        for g in self.bot.guilds:
            s = await self.compare_bots_users(g)
            if s == 0:
                success += 1
            elif s == 1:
                failed += 1
            else:
                passed += 1
        await ctx.send(
            f"**Finished cleaning guilds with a `bot:user` ratio higher than `2:1`**\n"
            f"Left `{success}` guilds\n"
            f"Failed Leaving: `{failed}` guilds\n"
            f"Ignored `{passed}` guilds\n"
        )

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, user: discord.User):
        """
        Blacklists or unblacklist a user
        """
        if user.id in self.config["blacklist"]:
            self.config["blacklist"].remove(user.id)
            await ctx.send(f"Unblacklisted user {user} from the bot")
        else:
            self.config["blacklist"].append(user.id)
            await ctx.send(f"Blacklisted user {user} from the bot")

    @commands.is_owner()
    @commands.command()
    async def update(self, ctx):
        """
        Checks if their is an update available
        """
        await ctx.send("Calling process to update! :up: :date: ")
        try:
            done = subprocess.run("git pull", shell=True, stdout=subprocess.PIPE, timeout=30)
            if done:
                message = done.stdout.decode()
                await ctx.send("`{}`".format(message))
                if message == "Already up-to-date.\n":
                    await ctx.send("No update available :no_entry:")
                else:
                    await ctx.send("Succesfully updated! Rebooting now :repeat: ")
                    await self.bot.logout()
        except subprocess.CalledProcessError:
            await ctx.send("Error updating! :exclamation: ")
        except subprocess.TimeoutExpired:
            await ctx.send("Error updating - Process timed out! :exclamation: ")

    @commands.is_owner()
    @commands.group(invoke_without_command=True)
    async def statuses(self, ctx):
        """
        Displays all custom statuses
        """
        await ctx.send(", ".join([s for s in self.statuses if not callable(s)]))

    @commands.is_owner()
    @statuses.command()
    async def add(self, ctx, *, status: str):
        """
        Adds a new status
        """
        if status not in self.statuses:
            self.statuses.append(status)
            self.config["additional_statuses"].append(status)
            await ctx.send("`Added new status!`")
        else:
            await ctx.send("`Status already exists dumb dumb...`")

    @commands.is_owner()
    @statuses.command()
    async def remove(self, ctx, *, status: str):
        """
        Removes a status
        """
        try:
            self.config["additional_statuses"].remove(status)
            self.statuses.remove(status)
            await ctx.send("`Removed status!`")
        except ValueError:
            await ctx.send("`Status did not exist`")

    def user_in_blacklist_check(self, ctx):
        """
        Checks whether a user is in the bot blacklist
        """
        user_id = ctx.author.id
        if user_id in self. config["blacklist"]:
            raise UserBlacklisted
        else:
            return True

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.compare_bots_users(guild)

    async def compare_bots_users(self, guild):
        b = 0
        u = 0
        for m in guild.members:
            if m.bot:
                b += 1
            else:
                u += 1
        self.logger.debug(f"{guild} [{guild.id}] Evaluated bot to user ratio for guild - Users: {u} Bots: {b}")
        if (b / 2) > u:
            self.logger.debug(f"{guild} [{guild.id}] ratio too high, attempting to leave")
            try:
                await guild.leave()
                self.logger.debug(f"{guild} [{guild.id}] left guild successfully")
                return 0  # left
            except discord.HTTPException:
                self.logger.debug(f"{guild} [{guild.id}] failed leaving guild")
                return 1  # error
        else:
            self.logger.debug(f"{guild} [{guild.id}] Ratio OK, not leaving guild")
            return 2  # nothing


setup = Admin.setup
