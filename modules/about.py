import datetime

import discord
from discord.ext import commands
from dinnerplate import BaseCog, has_embeds


class About(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)

    @commands.command()
    @has_embeds()
    async def info(self, ctx):
        """
        Information about GAF Bot
        """
        with ctx.channel.typing():
            embed = discord.Embed(title="Invite me to your server!", colour=discord.Colour.gold(),
                                  url="https://discordapp.com/oauth2/authorize?&client_id=173708503796416512&scope=bot&permissions=8",
                                  description=self.bot.description,
                                  timestamp=datetime.datetime.utcfromtimestamp(1493993514))

            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_author(name="GAF Bot", url="https://github.com/DiNitride/GAFBot")

            embed.add_field(name="Source Code", value="https://github.com/DiNitride/GAFBot")
            embed.add_field(name="Author", value="GAF Bot is written and maintained by DiNitride#7899")
            embed.add_field(name="Discord.py Version", value=discord.__version__)
            embed.add_field(name="The Never Ending GAF", value="GAF Bot is the bot of the awful community known as "
                                                               "The Never Ending GAF, which you can find out about at "
                                                               "http://www.neverendinggaf.com")

            await ctx.send(embed=embed)

    @commands.command()
    async def source(self, ctx):
        """
        Source Code
        """
        await ctx.send("`Source code available at` <https://github.com/DiNitride/GAFBot>")

    @commands.command()
    async def invite(self, ctx):
        """
        Invite link to add the bot to your guild
        """
        await ctx.send(
            "`Invite me to your server!` "
            "<https://discordapp.com/oauth2/authorize?&client_id=173708503796416512&scope=bot&permissions=8>")

    @commands.command()
    async def server(self, ctx):
        """
        Invite like to the bot's support server
        """
        await ctx.send("If you need help with the bot, feel free to join my server and ask! https://discord.gg/ddbFt7S")

    @commands.command()
    async def twitter(self, ctx):
        """
        Follow the bot on Twitter for status updates and announcements!
        """
        await ctx.send("https://twitter.com/_GAF_Bot")


setup = About.setup
