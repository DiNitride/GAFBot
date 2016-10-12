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
        with open("config/tags.json") as file:
            tags = json.load(file)
            file.close()
        with open("config/tags.json", "w") as file:
            if command in tags:
                del tags[command]
                save = json.dumps(tags)
                file.write(save)
                await self.bot.say("Tag %s has been removed :thumbsup:" %command)
            else:
                save = json.dumps(tags)
                file.write(save)
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
        with open("config/tags.json") as file:
            tags = json.load(file)
            taglist = "```Tags:"
            for x in tags.keys():
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
        with open("config/tags.json") as file:
            tags = json.load(file)
            if input in tags:
                await self.bot.say(tags[input])
            else:
                with open("config/tags.json", "w") as file:
                    tags[input] = output
                    save = json.dumps(tags)
                    file.write(save)
                    if output.startswith("http"):
                        await self.bot.say("Tag %s has been added with output <%s> :thumbsup:" % (input, output))
                    else:
                        await self.bot.say("Tag %s has been added with output %s :thumbsup:" % (input, output))

def setup(bot):
    bot.add_cog(Tags(bot))
