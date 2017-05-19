import json
import asyncio
from datetime import datetime

import discord
from discord.ext import commands

from utils import checks
from utils import reaction_menu


class Admin:

    def __init__(self, bot):
        self.bot = bot
        self.statuses = ["Long Live GAF", self.users_and_guilds, self.uptime]
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
        return "{}d{}h{}m{}s".format(days, hours, minutes, seconds)

    def commands_run(self):
        return "{} commands ran".format(self.bot.command_count)

    async def status_rotator(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for val in self.statuses:
                if callable(val):
                    val = val()
                await self.bot.change_presence(game=discord.Game(name=val))
                await asyncio.sleep(180)


def setup(bot):
    bot.add_cog(Admin(bot))
