import datetime

import discord
from discord.ext import commands

from bot.utils import checks


class Statistics:

    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=["stats"])
    @checks.has_embeds()
    async def statistics(self, ctx):
        """
        Shows the bot's session stats
        """
        _, days, hours, minutes, seconds = self.bot.calculate_uptime()
        users, channels = self.bot.sum_users_and_channels()
        with ctx.channel.typing():
            embed = discord.Embed(title="Bot Statistics since last startup", colour=discord.Colour.gold(),
                                  url="",
                                  description="",
                                  timestamp=datetime.datetime.utcfromtimestamp(1493993514))

            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_author(name="GAF Bot", url="https://github.com/DiNitride/GAFBot")

            embed.add_field(name="Uptime", value=f"{days} Days, {hours} Hours, "
                                                 f"{minutes} Minutes and {seconds} Seconds",
                            inline=False)
            embed.add_field(name="Commands ran", value=str(self.bot.command_count + 1), inline=False)
            embed.add_field(name="Total users (Non unique)", value=str(users), inline=False)
            embed.add_field(name="Channels", value=str(channels), inline=False)
            embed.add_field(name="Total Guilds", value=str(len(self.bot.guilds)), inline=False)

            await ctx.send(embed=embed)

    @commands.command()
    async def scout(self, ctx):
        """
        GAF Bot, what do your elf eyes see?
        """
        users, channels = self.bot.sum_users_and_channels()
        await ctx.send(f"`I can see {users} users in {channels} channels on {len(self.bot.guilds)} guilds`")

    @commands.command()
    async def uptime(self, ctx):
        """
        How long until I crash again?
        """
        _, days, hours, minutes, seconds = self.bot.calculate_uptime()
        await ctx.send(f"`{days} Days, {hours} Hours, {minutes} Minutes and {seconds} Seconds`")

    @commands.command()
    async def count(self, ctx):
        """
        Commands ran since boot
        """
        await ctx.send("`{} commands ran since last boot`".format(self.bot.command_count + 1))


def setup(bot):
    bot.add_cog(Statistics(bot))
