import asyncio

import discord
from discord.ext import commands
import dateparser
from lxml import etree
import html2text

from bot.utils import net, checks


class CSGO:

    def __init__(self, bot):
        self.bot = bot
        # self.bg_task = self.bot.loop.create_task(self.csgo_update_loop())

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
        Enables tracking CS:GO updates for your guild.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["csgo_updates"] = True
        guild_config["csgo_updates_channel"] = ctx.channel.id
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, tracking CS:GO updates in channel #{}`".format(ctx.channel))

    @csupdates.command()
    async def stop(self, ctx):
        """
        Disables tracking CS:GO updates on your guild.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["csgo_updates"] = False
        guild_config["csgo_updates_channel"] = ""
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, no longer tracking CS:GO updates`")

    @csupdates.command()
    async def set(self, ctx):
        """
        Set's the channel in which the updates will be posted.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["csgo_updates_channel"] = ctx.channel.id
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, tracking channel set to #{}`".format(ctx.channel))

    async def csgo_update_loop(self):
        await self.bot.wait_until_ready()
        self.bot.logger.debug("Run CS:GO Update Check")
        while not self.bot.is_closed():
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
                    guild_config = await self.bot.get_guild_config(guild.id)
                    if guild_config["csgo_updates"] is True:
                        channel = discord.utils.get(guild.channels, id=guild_config["csgo_updates_channel"])
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
                            self.bot.logger.debug("Sent update informaton to guild {} in channel #{}".format(guild, channel))
                if i == 0:
                    self.bot.config["csgo_last_pub"] = element[2].text
                    await self.bot.update_config()
            await asyncio.sleep(60 * 5)


def setup(bot):
    bot.add_cog(CSGO(bot))
