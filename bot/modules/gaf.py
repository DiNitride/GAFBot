import asyncio

from discord.ext import commands
import discord
import dateparser
import html2text
from lxml import etree

from bot.utils import checks, net


class GAF:

    def __init__(self, bot):
        self.bot = bot
        self.bg_task = self.bot.loop.create_task(self.update_check())

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
        await ctx.send(content="<@&172426880543227904> <@&262334316611239937>, chill? - {}".format(ctx.author), file=discord.File("bot/resources/chill.jpg"))
        await ctx.message.delete()

    @gaf.group(invoke_without_subcommand=True)
    @checks.perms_manage_messages()
    async def rss(self, ctx):
        """
        Allows you to manage RSS feed for GAF Steam Annoucements
        """
        pass

    @rss.command()
    async def track(self, ctx):
        """
        Enables tracking GAF RSS updates for your guild.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["feeds"]["gaf"]["enabled"] = True
        guild_config["feeds"]["gaf"]["channel"] = ctx.channel.id
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, tracking GAF RSS updates in channel #{}`".format(ctx.channel))

    @rss.command()
    async def stop(self, ctx):
        """
        Disables tracking GAF RSS updates on your guild.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["feeds"]["gaf"]["enabled"] = False
        guild_config["feeds"]["gaf"]["enabled"] = ""
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, no longer tracking GAF RSS updates`")

    @rss.command()
    async def set(self, ctx):
        """
        Set's the channel in which the updates will be posted.
        """
        guild_config = await self.bot.get_guild_config(ctx.guild.id)
        guild_config["feeds"]["gaf"]["enabled"] = ctx.channel.id
        await self.bot.set_guild_config(ctx.guild.id, guild_config)
        await ctx.send("`Okay, tracking channel set to #{}`".format(ctx.channel))

    async def update_check(self):
        await self.bot.wait_until_ready()
        self.bot.logger.debug("Started GAF Steam Announcement RSS Update Check Loop")
        while not self.bot.is_closed():
            response, _, code = await net.get_url("http://steamcommunity.com/groups/TheNeverEndingGAF/rss/")
            xml = await response.read()
            root = etree.fromstring(xml)
            last_pub = dateparser.parse(self.bot.config["pub_dates"]["gaf"])
            new_posts = []
            for element in root.xpath("//item"):
                post_pub = dateparser.parse(element[3].text)
                if post_pub > last_pub:
                    new_posts.append(element)

            # Iterate over new posts
            for i, p in reversed(list(enumerate(new_posts))):
                # Update date if it's the newest post. Should be last elemen iterated through
                if i == 0:
                    self.bot.config["pub_dates"]["gaf"] = p[3].text
                    await self.bot.update_config()
                    self.bot.logger.debug("Updated GAF pub date")

                # Post to guilds
                for guild in self.bot.guilds:
                    guild_config = await self.bot.get_guild_config(guild.id)
                    if guild_config["feeds"]["gaf"]["enabled"]:
                        channel = discord.utils.get(guild.channels, id=guild_config["feeds"]["gaf"]["channel"])
                        with channel.typing():
                            if len(html2text.html2text(p.find("description").text)) > 1900:
                                content = html2text.html2text(p.find("description").text[:1900]) + ". . ."
                            else:
                                content = html2text.html2text(p.find("description").text)
                            embed = discord.Embed(
                                title="{}".format(p.find("title").text),
                                colour=discord.Colour.gold(),
                                url="{}".format(p.find("link").text),
                                timestamp=dateparser.parse(p[3].text),
                                description=content
                            )
                            await channel.send(embed=embed)
                            self.bot.logger.debug(f"Sent new GAF Steam Announcement to guild {guild} channel {channel}")

            await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(GAF(bot))