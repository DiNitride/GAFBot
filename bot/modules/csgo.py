import asyncio

import discord
from discord.ext import commands
import dateparser
from lxml import etree
import html2text

from utils import net, checks


class CSGO:

    def __init__(self, bot):
        self.bot = bot
        self.bg_task = self.bot.loop.create_task(self.csgo_update_loop())

    @commands.group()
    @checks.perms_manage_messages()
    async def csupdates(self, ctx):
        """
        Manages tracking CS:GO updates for your guild. BROKEN
        """
        pass

    @csupdates.command()
    async def track(self, ctx):
        """
        Enables tracking CS:GO updates for your server.
        """
        server = await self.bot.get_server_data(ctx.guild.id)
        server["csgo_updates"] = True
        server["csgo_updates_channel"] = ctx.channel.id
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Okay, tracking CS:GO updates in channel #{}`".format(ctx.channel))

    @csupdates.command()
    async def stop(self, ctx):
        """
        Disables tracking CS:GO updates on your server.
        """
        server = await self.bot.get_server_data(ctx.guild.id)
        server["csgo_updates"] = False
        server["csgo_updates_channel"] = ""
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Okay, no longer tracking CS:GO updates`")

    @csupdates.command()
    async def set(self, ctx):
        """
        Set's the channel in which the updates will be posted.
        """
        server = await self.bot.get_server_data(ctx.guild.id)
        server["csgo_updates_channel"] = ctx.channel.id
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Okay, tracking channel set to #{}`".format(ctx.channel))

    async def csgo_update_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.bot.log.debug("Run CS:GO Update Check")
            response, _, code = await net.get_url("http://blog.counter-strike.net/index.php/category/updates/feed/")
            xml = await response.read()
            root = etree.fromstring(xml)
            last_pub = dateparser.parse(self.bot.config["csgo_last_pub"])
            new_posts = []
            for element in root.xpath("//item"):
                post_pub = dateparser.parse(element[2].text)
                if post_pub <= last_pub:
                    break
                elif post_pub > last_pub:
                    new_posts.append(element)
            for i, element in reversed(list(enumerate(new_posts))):
                for guild in self.bot.guilds:
                    server = await self.bot.get_server_data(guild.id)
                    if server["csgo_updates"] is True:
                        channel = discord.utils.get(guild.channels, id=server["csgo_updates_channel"])
                        with channel.typing():
                            if len(html2text.html2text(element.find("content:encoded", namespaces={"content": "http://purl.org/rss/1.0/modules/content/"}).text)) > 1900:
                                content = html2text.html2text(element.find("content:encoded", namespaces={"content": "http://purl.org/rss/1.0/modules/content/"}).text[:1900]) + ". . ."
                            else:
                                content = html2text.html2text(element.find("content:encoded", namespaces={"content": "http://purl.org/rss/1.0/modules/content/"}).text)
                            embed = discord.Embed(
                                title="{}".format(element.find("title").text),
                                colour=discord.Colour.gold(),
                                url="{}".format(element.find("link").text),
                                timestamp=dateparser.parse(element[2].text),
                                description=content
                            )
                            await channel.send(embed=embed)
                            self.bot.log.debug("Sent update informaton to guild {} in channel #{}".format(guild, channel))
                if i == 0:
                    await self.bot.update_config("csgo_last_pub", element[2].text)
            await asyncio.sleep(60 * 5)


def setup(bot):
    bot.add_cog(CSGO(bot))
