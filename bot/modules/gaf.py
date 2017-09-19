from discord.ext import commands
import discord

import dateparser
import html2text
from lxml import etree

from bot.utils import checks, net


class GAF:

    def __init__(self, bot):
        self.bot = bot
        # self.bg_task = self.bot.loop.create_task(self.gaf_update_loop())

    @commands.group(invoke_without_command=True)
    async def gaf(self, ctx):
        """
        Information on The Never Ending GAF
        """
        await ctx.send("The Never Ending GAF is a small group of idiots that play games and insult each other. "
                       "\nWe reside on our Discord server, usually in the beloved cesspool intelligently "
                       "titled \"Channel 1\".\nFeel free to pop by, probably get told to piss off, and maybe "
                       "play some games."
                       "\nMore info and invite links: <http://www.neverendinggaf.com>")

    @gaf.command()
    async def website(self, ctx):
        """
        Link to The Never Ending GAF's Website
        """
        await ctx.send("<http://www.neverendinggaf.com>")

    @gaf.command()
    async def invite(self, ctx):
        """
        GAF Guild Invite
        """
        await ctx.send("<http://discord.neverendinggaf.com>")

    @commands.command()
    @checks.is_gaf_server()
    async def chill(self, ctx):
        """
        Channel 1 and chill?
        """
        await ctx.send(content="<@&172426880543227904> <@&262334316611239937>, chill? - {}".format(ctx.author), file=discord.File("resources/chill.jpg"))
        await ctx.message.delete()

    @gaf.group(invoke_without_subcommand=True)
    @checks.perms_manage_messages()
    async def rss(self, ctx):
        """
        Allows you to manage RSS feed for GAF Steam Annoucements
        """
        server = await self.bot.get_server_data(ctx.guild.id)
        if server["gaf_steam_rss"] is True:
            channel = discord.utils.get(ctx.guild.channels, id=server["gaf_steam_rss_channel"])
            await ctx.send("GAF RSS Tracking is enabled in channel #{}".format(channel))
        else:
            await ctx.send("GAF RSS Tracking is not enabled")


    @rss.command()
    async def track(self, ctx):
        """
        Enables tracking GAF RSS updates for your server.
        """
        server = await self.bot.get_server_data(ctx.guild.id)
        server["gaf_steam_rss"] = True
        server["gaf_steam_rss_channel"] = ctx.channel.id
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Okay, tracking GAF RSS updates in channel #{}`".format(ctx.channel))

    @rss.command()
    async def stop(self, ctx):
        """
        Disables tracking GAF RSS updates on your server.
        """
        server = await self.bot.get_server_data(ctx.guild.id)
        server["gaf_steam_rss"] = False
        server["gaf_steam_rss_channel"] = ""
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Okay, no longer tracking GAF RSS updates`")

    @rss.command()
    async def set(self, ctx):
        """
        Set's the channel in which the updates will be posted.
        """
        server = await self.bot.get_server_data(ctx.guild.id)
        server["gaf_steam_rss_channel"] = ctx.channel.id
        await self.bot.update_server_data(ctx.guild.id, server)
        await ctx.send("`Okay, tracking channel set to #{}`".format(ctx.channel))

    async def gaf_update_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.bot.log.debug("Run GAF RSS Update Check")
            response, _, code = await net.get_url("http://steamcommunity.com/groups/TheNeverEndingGAF/rss/")
            xml = await response.read()
            root = etree.fromstring(xml)
            last_pub = dateparser.parse(self.bot.config["gaf_last_pub"])
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
                    if server["gaf_steam_rss"] is True:
                        channel = discord.utils.get(guild.channels, id=server["gaf_steam_rss_channel"])
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
                            self.bot.log.debug("Sent GAF update informaton to guild {} in channel #{}".format(guild, channel))
                if i == 0:
                    await self.bot.update_config("gaf_last_pub", element[3].text)
            await asyncio.sleep(60 * 5)


def setup(bot):
    bot.add_cog(GAF(bot))