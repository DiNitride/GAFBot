import asyncio

import discord
from discord.ext import commands
import dateparser
from lxml import etree
import html2text

from utils import net, checks


class PUBG:

    def __init__(self, bot):
        self.bot = bot
        self.bg_task = self.bot.loop.create_task(self.pubg_update_loop())

    @commands.group()
    async def pubgupdates(self, ctx):
        """
        Manages tracking PUBG updates for your guild.
        """
        pass

    @pubgupdates.command()
    async def track(self, ctx):
        """
        Enables tracking PUBG updates for your server.
        """
        server = await self.bot.get_server_data(ctx.guild.id)
        server["pubg_updates"] = True
        server["pubg_updates_channel"] = ctx.channel.id
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Okay, tracking PUBG updates in channel #{}`".format(ctx.channel))

    @pubgupdates.command()
    async def stop(self, ctx):
        """
        Disables tracking PUBG updates on your server.
        """
        server = await self.bot.get_server_data(ctx.guild.id)
        server["pubg_updates"] = False
        server["pubg_updates_channel"] = ""
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Okay, no longer tracking PUBG updates`")

    @pubgupdates.command()
    async def set(self, ctx):
        """
        Set's the channel in which the updates will be posted.
        """
        server = await self.bot.get_server_data(ctx.guild.id)
        server["pubg_updates_channel"] = ctx.channel.id
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Okay, tracking channel set to #{}`".format(ctx.channel))

    async def pubg_update_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.bot.log.debug("Run PUBG Update Check")
            response, _, code = await net.get_url("https://steamcommunity.com/games/578080/rss/")
            xml = await response.read()
            root = etree.fromstring(xml)
            last_pub = dateparser.parse(self.bot.config["pubg_last_pub"])
            new_posts = []
            for element in root.xpath("//item"):
                post_pub = dateparser.parse(element[3].text)
                if post_pub <= last_pub:
                    break
                elif post_pub > last_pub:
                    new_posts.append(element)
            for i, element in reversed(list(enumerate(new_posts))):
                for guild in self.bot.guilds:
                    server = await self.bot.get_server_data(guild.id)
                    if server["pubg_updates"] is True:
                        channel = discord.utils.get(guild.channels, id=server["pubg_updates_channel"])
                        with channel.typing():
                            if len(html2text.html2text(element.find("description").text)) > 1900:
                                content = html2text.html2text(element.find("description").text[:1900]) + ". . ."
                            else:
                                content = html2text.html2text(element.find("description").text)
                            embed = discord.Embed(
                                title="{}".format(element.find("title").text),
                                colour=discord.Colour.gold(),
                                url="{}".format(element.find("link").text),
                                timestamp=dateparser.parse(element[3].text),
                                description=content
                            )
                            await channel.send(embed=embed)
                            self.bot.log.debug("Sent PUBG update informaton to guild {} in channel #{}".format(guild, channel))
                if i == 0:
                    await self.bot.update_config("pubg_last_pub", element[3].text)
            await asyncio.sleep(60 * 5)


def setup(bot):
    bot.add_cog(PUBG(bot))
