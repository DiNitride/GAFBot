from datetime import datetime

import discord
from discord.ext import commands


class Statistics:

    def __init__(self, bot):
        self.bot = bot
        self.scout.enabled = bot.modules["statistics"]
        self.uptime.enabled = bot.modules["statistics"]

    @commands.command()
    async def scout(self, ctx):
        """GAF Bot, what do your elf eyes see?"""
        _users = 0
        _channels = 0
        for user in self.bot.get_all_members():
            _users += 1
        for channel in self.bot.get_all_channels():
            _channels += 1
        await ctx.send("I can see {} users in {} channels on {} guilds".format(_users, _channels, len(self.bot.guilds)))
        self.bot.cmd_log(ctx, "Scouting for girls")

    @commands.command()
    async def uptime(self, ctx):
        """How long until I crash again?"""
        currentTime = datetime.now()
        uptime = currentTime - self.bot.start_time
        days = int(uptime.days)
        hours = int(uptime.seconds / 3600)
        minutes = int((uptime.seconds % 3600) / 60)
        seconds = int((uptime.seconds % 3600) % 60)
        await ctx.send("`{} Days, {} Hours, {} Minutes and {} Seconds`".format(days, hours, minutes, seconds))
        self.bot.cmd_log(ctx, "Uptime")


def setup(bot):
    bot.add_cog(Statistics(bot))
