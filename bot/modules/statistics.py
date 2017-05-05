import discord
from discord.ext import commands
from utils import checks


class Statistics:

    def __init__(self, bot):
        self.bot = bot
        self.scout.enabled = bot.modules["statistics"]

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


def setup(bot):
    bot.add_cog(Statistics(bot))