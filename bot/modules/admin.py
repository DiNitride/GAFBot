import discord
from discord.ext import commands
from utils import checks
from utils import reaction_menu
import json
import asyncio


class Admin:

    def __init__(self, bot):
        self.bot = bot
        self.statuses = ["Long Live GAF", self.users_and_guilds()]
        self.bg_task = self.bot.loop.create_task(self.status_rotator())

    def users_and_guilds(self):
        _users = 0
        for user in self.bot.get_all_members():
            _users += 1
        return "{} users in {} guilds".format(_users, len(self.bot.guilds))

    async def status_rotator(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for val in self.statuses:
                await self.bot.change_presence(game=discord.Game(name=val))
                await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(Admin(bot))
