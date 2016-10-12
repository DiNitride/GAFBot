import discord
from discord.ext import commands
import random
import json
from utils import checks

class Misc():
    def __init__(self, bot):
        self.bot = bot

    # Random delet this image
    # Couldn't be bothered to write the meme comand to do random images for a meme
    # so this can stay separate
    @commands.command()
    async def deletthis(self):
        """Shows a random delet this image
        Usage:
        $deletthis"""
        deletthisimages=["http://i.imgur.com/ccC9nzl.jpg",
                         "http://i.imgur.com/o3n6Kms.jpg",
                         "http://i.imgur.com/WK8o9Nr.jpg",
                         "http://i.imgur.com/VwpcSoJ.jpg",
                         "http://i.imgur.com/nXEVoFo.jpg",
                         "http://i.imgur.com/XTdGXOX.png",
                         "http://i.imgur.com/kZTV9af.jpg",
                         "http://i.imgur.com/h4mtF8M.jpg"]
        delet=random.choice(deletthisimages)
        await self.bot.say(delet)

    # F to pay resepects
    # This is separate because I want it to be
    #####################################################
    #                                                   #
    # ###### ###### ###### ###### ###### ###### ######  #
    # ##  ## ###### ###### ###### ###### ###### ######  #
    # ###### ##     ##     ##  ## ##     ##       ##    #
    # ####   ###### ###### ###### ###### ##       ##    #
    # #####  ###### ###### ##     ###### ##       ##    #
    # ## ### ##         ## ##     ##     ##       ##    #
    # ##  ## ###### ###### ##     ###### ######   ##    #
    # ##  ## ###### ###### ##     ###### ######   ##    #
    #                                                   #
    #####################################################
    @commands.command()
    async def f(self):
        """Pay respects"""
        await self.bot.say("Respect")

def setup(bot):
    bot.add_cog(Misc(bot))
