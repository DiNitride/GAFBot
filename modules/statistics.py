import datetime

import discord
from discord.ext import commands
from dinnerplate import BaseCog, has_embeds


class Statistics(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)

    @commands.command(aliases=["stats"])
    @has_embeds()
    async def statistics(self, ctx):
        """
        Shows the bot's session stats
        """
        cmd_count, guilds, channels, users = self.bot.stats
        seconds, minutes, hours, days = self.bot.uptime[1]

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
            embed.add_field(name="Commands ran", value=str(cmd_count + 1), inline=False)
            embed.add_field(name="Total Unique Users", value=str(users), inline=False)
            embed.add_field(name="Channels", value=str(channels), inline=False)
            embed.add_field(name="Total Guilds", value=str(guilds), inline=False)

            await ctx.send(embed=embed)


setup = Statistics.setup
