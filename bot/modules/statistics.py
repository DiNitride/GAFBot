import datetime

import discord
from discord.ext import commands

from utils import checks


class Statistics:

    def __init__(self, bot):
        self.bot = bot

    def users_and_channels(self):
        users = sum(1 for user in self.bot.get_all_members())
        channels = sum(1 for channel in self.bot.get_all_channels())
        return users, channels

    def calculate_uptime(self):
        currentTime = datetime.datetime.now()
        uptime = currentTime - self.bot.start_time
        days = int(uptime.days)
        hours = int(uptime.seconds / 3600)
        minutes = int((uptime.seconds % 3600) / 60)
        seconds = int((uptime.seconds % 3600) % 60)
        return days, hours, minutes, seconds

    @commands.command(aliases=["stats"])
    @checks.has_embeds()
    async def statistics(self, ctx):
        """
        Shows the bot's session stats
        """
        days, hours, minutes, seconds = self.calculate_uptime()
        users, channels = self.users_and_channels()
        with ctx.channel.typing():
            embed = discord.Embed(title="Bot Statistics since last startup", colour=discord.Colour.gold(),
                                  url="",
                                  description="",
                                  timestamp=datetime.datetime.utcfromtimestamp(1493993514))

            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_author(name="GAF Bot", url="https://github.com/DiNitride/GAFBot")

            embed.add_field(name="Uptime", value="{} Days, {} Hours, {} Minutes and {} Seconds".format(days, hours, minutes, seconds), inline=False)
            embed.add_field(name="Commands ran", value=self.bot.command_count + 1, inline=False)
            embed.add_field(name="Total users (Non unique)", value=users, inline=False)
            embed.add_field(name="Channels", value=channels, inline=False)
            embed.add_field(name="Total Guilds", value=str(len(self.bot.guilds)), inline=False)

            await ctx.send(embed=embed)

    @commands.command()
    async def scout(self, ctx):
        """
        GAF Bot, what do your elf eyes see?
        """
        users, channels = self.users_and_channels()
        await ctx.send("`I can see {} users in {} channels on {} guilds`".format(users, channels, len(self.bot.guilds)))

    @commands.command()
    async def uptime(self, ctx):
        """
        How long until I crash again?
        """
        days, hours, minutes, seconds = self.calculate_uptime()
        await ctx.send("`{} Days, {} Hours, {} Minutes and {} Seconds`".format(days, hours, minutes, seconds))

    @commands.command()
    async def count(self, ctx):
        """
        Commands ran since boot
        """
        await ctx.send("`{} commands ran since last boot`".format(self.bot.command_count + 1))


def setup(bot):
    bot.add_cog(Statistics(bot))
