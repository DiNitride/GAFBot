import discord
from discord.ext import commands
import json
from utils import checks

class Tags():
    def __init__(self, bot):
        self.bot = bot

    # Allowed the removal of a tag from the data file
    @commands.command(hidden=True)
    @commands.check(checks.is_owner)
    async def rmtag(self, command: str):
        """Removes a tag
        Usage:
        $rmtag tag"""
        if command in self.bot.tags:
            del self.bot.tags[command]
            await self.bot.say("Tag {} has been removed :thumbsup:".format(command))
        else:
            await self.bot.say("Tag not registered, could not delete :thumbsdown: ")

    # Lists all the tags currently stored
    # Command output looks really ugly
    # Needs make-over
    @commands.command()
    @commands.check(checks.is_owner)
    async def tags(self):
        """Lists the tags added
        Usage:
        $tags"""
        taglist = "```Tags:"
        for x in self.bot.tags.keys():
            taglist = "%s\n- %s" %(taglist, x)
        await self.bot.say("{0} ```".format(taglist))

    # Allows the user to find and execute a tags
    @commands.command()
    @commands.check(checks.is_owner)
    async def tag(self, input : str, *, output : str = None):
        """Adds or displays a tag
        Usage:
        $tag tag_name tag_data
        If 'tag_name' is a saved tag it will display that, else it will
        create a new tag using 'tag_data'"""
        if input in self.bot.tags:
            await self.bot.say(self.bot.tags[input])
        else:
            self.bot.tags[input] = output
            if output.startswith("http"):
                await self.bot.say("Tag {} has been added with output <{}> :thumbsup:" .format(input, output))
            else:
                await self.bot.say("Tag {} has been added with output {} :thumbsup:".format(input, output))

def setup(bot):
    bot.add_cog(Tags(bot))
