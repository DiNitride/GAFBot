import discord
from discord.ext import commands
import feedparser
import asyncio
from utils import checks

class RSS():
    def __init__(self, bot):
        self.bot = bot
        self.rss_updater = bot.loop.create_task(self.rss())
        self.redditrss_updater = bot.loop.create_task(self.redditrss())

    async def rss(self):
        while True:
            d = feedparser.parse('http://steamcommunity.com/groups/TheNeverEndingGAF/rss/')
            for post in d.entries:
                with open("posted.txt", 'r') as f:
                    posted = [line.rstrip('\n') for line in f]
                f.close()
                if post.title not in posted:
                    print("Posted: " + post.title + "\n" + post.link + "\n")
                    channel = discord.Object('172425708507758594')
                    await self.bot.send_message(channel, "==============================\n@everyone\n*ANNOUNCEMENT*\n**{0.title}**\nRead: <{0.link}>\n==============================\n".format(post))
                    with open("posted.txt", 'a') as f:
                        f.write(post.title + '\n')
                    f.close()
            await asyncio.sleep(300)

    async def redditrss(self):
        while True:
            d = feedparser.parse('https://www.reddit.com/r/TheNeverEndingGAF/.rss')
            for post in d.entries:
                with open("subreddit.txt", 'r') as f:
                    posted = [line.rstrip('\n') for line in f]
                f.close()
                if post.title not in posted:
                    print("Posted: " + post.title + "\n" + post.link + "\n")
                    channel = discord.Object('172425708507758594')
                    await self.bot.send_message(channel,"==============================\n*New Reddit Post:*\n**{0.title}**\nRead: <{0.link}>\n==============================\n".format(post))
                    with open("subreddit.txt", 'a') as f:
                        f.write(post.title + '\n')
                    f.close()
            await asyncio.sleep(900)

    @commands.command(hidden=True)
    @commands.check(checks.is_owner)
    async def forcerss(self):
        """Forces an RSS pull"""
        d = feedparser.parse('http://steamcommunity.com/groups/TheNeverEndingGAF/rss/')
        for post in d.entries:
            with open("posted.txt", 'r') as f:
                posted = [line.rstrip('\n') for line in f]
            f.close()
            if post.title not in posted:
                print("Posted: " + post.title + "\n" + post.link + "\n")
                channel = discord.Object('172425708507758594')
                await self.bot.send_message(channel,"==============================\n@everyone\n*ANNOUNCEMENT*\n**{0.title}**\nRead: <{0.link}>\n==============================\n".format(post))
                with open("posted.txt", 'a') as f:
                    f.write(post.title + '\n')
                f.close()
        print("Run: Force RSS")

    @commands.command(hidden=True)
    @commands.check(checks.is_owner)
    async def forceredditrss(self):
        """Forces an RSS pull"""
        d = feedparser.parse('https://www.reddit.com/r/TheNeverEndingGAF/.rss')
        for post in d.entries:
            with open("subreddit.txt", 'r') as f:
                posted = [line.rstrip('\n') for line in f]
            f.close()
            if post.title in posted:
                print(post.title + " already posted")
            else:
                print("Posted: " + post.title + "\n" + post.link + "\n")
                channel = discord.Object('172425708507758594')
                await self.bot.send_message(channel,
                                       "==============================\n*New Reddit Post:*\n**{0.title}**\nRead: <{0.link}>\n==============================\n".format(
                                           post))
                with open("subreddit.txt", 'a') as f:
                    f.write(post.title + '\n')
                f.close()
        print("Run: Force Reddit RSS")

def setup(bot):
    bot.add_cog(RSS(bot))