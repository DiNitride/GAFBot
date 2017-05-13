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
        _users = 0
        for user in self.bot.get_all_members():
            _users += 1
        return "{} users in {} guilds".format(_users, len(self.bot.guilds))

    def uptime(self):
        currentTime = datetime.now()
        uptime = currentTime - self.bot.start_time
        days = int(uptime.days)
        hours = int(uptime.seconds / 3600)
        minutes = int((uptime.seconds % 3600) / 60)
        seconds = int((uptime.seconds % 3600) % 60)
        if days != 0:
            return "{} Days, {} Hours, {} Minutes and {} Seconds".format(days, hours, minutes, seconds)
        elif hours != 0:
            return "{} Hours, {} Minutes and {} Seconds".format(hours, minutes, seconds)
        else:
            return "{} Minutes and {} Seconds".format(minutes, seconds)

    async def status_rotator(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for val in self.statuses:
                if callable(val):
                    val = val()
                await self.bot.change_presence(game=discord.Game(name=val))
                self.bot.log.debug("Update game to {}".format(val))
                await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(Admin(bot))
