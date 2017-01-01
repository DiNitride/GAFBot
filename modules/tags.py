import discord
from discord.ext import commands
import json
from utils import checks
import datetime

def time():
    return datetime.datetime.now().strftime("%b/%d/%Y %H:%M:%S")

class Tags():
    def __init__(self, bot):
        self.bot = bot


    @commands.group(invoke_without_command=True)
    async def tag(self, *, tag: str = None):
        """$help tag for more.
        Finds a tag and outputs it
        Usage: $tag Birdy
        > Will output tag birdy"""

        if tag is None:
            return

        tag = tag.lower()

        if tag in self.bot.tags:
            await self.bot.say(self.bot.tags[tag]["content"])
        else:
            await self.bot.say("No tag found :grey_question:")

    @tag.command(pass_context=True, name="del")
    async def _del(self, ctx, *, tag: str = None):
        """Deletes a tag.
        Usage: $tag del Fuyu"""
        tag = tag.lower()
        if tag is None:
            return

        if tag in self.bot.tags.keys():
            if (self.bot.tags[tag]["owner"] == ctx.message.author.id) or (self.bot.config["ids"]["owner"] == ctx.message.author.id):
                self.bot.tags.pop(tag)
                await self.bot.say("Tag {} has been deleted :bomb:".format(tag))
            else:
                await self.bot.say("You do not own this tag")
                return

    @tag.command(pass_context=True, name="add")
    async def _add(self, ctx, *, tag: str = None):
        """Creates a tag.
        Usage:
        $tag add Fuyu
        [In next message sent]
        Is a dictator

        > Will create tag 'Fuyu' with output of 'Is a dictator'"""

        if tag is None:
            await self.bot.say("You must provide a tag name :exclamation: ")
            return

        tag = tag.lower()

        if tag in self.bot.tags.keys():
            await self.bot.say("A tag already exists with that name")
            return

        await self.bot.say("Please enter the content for the tag")

        tag_content = await self.bot.wait_for_message(timeout=180, author=ctx.message.author, channel=ctx.message.channel)

        if tag_content is None:
            await self.bot.say("Timed out, aborted creating tag :broken_heart:")
            return

        await self.bot.delete_message(ctx.message)

        if tag_content.content.startswith("http"):
            await self.bot.say("Tag {} has been added with output <{}> :thumbsup:" .format(tag, tag_content.content))
        else:
            await self.bot.say("Tag {} has been added with output {} :thumbsup:".format(tag, tag_content.content))
        author = str(ctx.message.author)
        self.bot.tags[tag] = {"content": tag_content.content, "owner": {"id": ctx.message.author.id, "name": author}, "server": ctx.message.server.name, "date": time()}

    @tag.command()
    async def info(self, *, tag: str = None):
        """Provides info on a tag.
        Usgae: $tag info Birdy"""
        if tag is None:
            return

        tag = tag.lower()

        if tag in self.bot.tags.keys():
            tag_data = self.bot.tags[tag]
            message = "```\nInfo on tag : {}\nContent: {}\nAuthor: {}\nCreated on: {}\n```".format(tag, tag_data["content"], tag_data["owner"]["name"], tag_data["date"])
            await self.bot.say(message)

    @commands.command(pass_context=True)
    async def tags(self, ctx):
        """Lists your tags.
        Usage: $tags"""
        _temp = ""
        for tag in self.bot.tags.keys():
            if self.bot.tags[tag]["owner"]["id"] == ctx.message.author.id:
                _temp += "{}\n".format(tag)
        await self.bot.say("```\nTags for {}:\n{}\n```".format(ctx.message.author.name, _temp))

def setup(bot):
    bot.add_cog(Tags(bot))
