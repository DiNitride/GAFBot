import datetime
import subprocess
import inspect

import discord
from discord.ext import commands

from bot.utils import checks


class Core:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.has_embeds()
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
        await ctx.send("`My source code is open source and available at <https://github.com/DiNitride/GAFBot>")

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
        await ctx.send("<http://discord.bot.neverendinggaf.com> - https://discord.gg/ddbFt7S")

    @commands.command()
    async def twitter(self, ctx):
        """
        Follow the bot on Twitter for status updates and announcements!
        """
        await ctx.send("https://twitter.com/_GAF_Bot")

    @commands.command()
    async def ping(self, ctx):
        """
        Pong
        """
        await ctx.send(f"Pong! :ping_pong: **{self.bot.latency * 1000:.0f}ms**")

    @commands.command()
    @checks.is_owner()
    async def update(self, ctx):
        """
        Updates the bot from the Github repo
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

    @commands.command()
    @checks.is_owner()
    async def blacklist(self, user: discord.User):
        """
        Blacklists or unblacklist a user
        """
        if user.id in int(self.bot.config["user_blacklist"]):
            self.bot.config["user_blacklist"].remove(user.id)
        else:
            self.bot.config["user_blacklist"].add(user.id)
            await self.bot.update_config()

    @commands.command()
    async def f(self, ctx):
        """
        Pays respects
        """

    @commands.command()
    @checks.is_owner()
    async def debug(self, ctx, *, code):
        """
        Evaluates a line of code provided
        """
        code = code.strip("` ")
        try:
            result = eval(code)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            await ctx.send("```py\nInput: {}\n{}: {}```".format(code, type(e).__name__, e))
        else:
            await ctx.send("```py\nInput: {}\nOutput: {}\n```".format(code, result))
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Core(bot))
