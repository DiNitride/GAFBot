import discord
from discord.ext import commands
import random
import json
from utils import checks

class Misc():
    def __init__(self, bot):
        self.bot = bot

    ##################
    ## Meme Section ##
    ##################

    # Allows the addition of a meme to the data file
    # Requires the command and ouput
    # Can only be used by bot owner
    @checks.is_owner()
    @commands.command(hidden=True)
    async def addmeme(self, command : str, *, output : str):
        with open("memes.txt") as file:
            memes = json.load(file)
            file.close()
        with open("memes.txt","w") as file:
            memes[command] = output
            save = json.dumps(memes)
            file.write(save)
            if output.startswith("http"):
                await self.bot.say("Meme %s has been added with output <%s> :thumbsup:" %(command, output))
            else:
                await self.bot.say("Meme %s has been added with output %s :thumbsup:"  % (command, output))
            print("Registered meme %s" % command)

    # Allowed the removal of a meme from the data file
    @checks.is_owner()
    @commands.command(hidden=True)
    async def delmeme(self, command: str):
        with open("memes.txt") as file:
            memes = json.load(file)
            file.close()
        with open("memes.txt", "w") as file:
            if command in memes:
                del memes[command]
                save = json.dumps(memes)
                file.write(save)
                await self.bot.say("Meme %s has been removed :thumbsup:" %command)
                print("Unregistered meme %s" %command)
            else:
                save = json.dumps(memes)
                file.write(save)
                await self.bot.say("Meme not registered, could not delete :thumbsdown: ")
                print("Meme unregister error, no meme %s" %command)

    # Lists all the memes currently stored
    # Command output looks really ugly
    # Needs make-over
    @commands.command()
    async def memes(self):
        """Lists the memes availible to output"""
        with open("memes.txt") as file:
            memes = json.load(file)
            memelist = "```Memes:"
            for x in memes.keys():
                memelist = "%s\n- %s" %(memelist, x)
            await self.bot.say("%s```" %memelist)
            print("Run: Memes Listed")

    # Allows the user to find and execute a meme
    @commands.command()
    async def meme(self, input):
        """Outputs a selected meme"""
        with open("memes.txt") as file:
            memes = json.load(file)
            if input in memes:
                await self.bot.say(memes[input])
                print("Run: Meme %s" %input)
            else:
                await self.bot.say("That's not a registered meme, pm bot owner to get it registered. :zzz: ")
                print("Unregistered meme %s executed" %input)

    #######################
    ## Copypasta Section ##
    #######################

    # Allows the addition of a meme to the data file
    # Requires the command and ouput
    # Can only be used by bot owner
    @checks.is_owner()
    @commands.command(hidden=True)
    async def addpasta(self, command : str, *, output : str):
        with open("copypastas.txt") as file:
            pasta = json.load(file)
            file.close()
        with open("copypastas.txt","w") as file:
            pasta[command] = output
            save = json.dumps(pasta)
            file.write(save)
            if output.startswith("http"):
                await self.bot.say("Copypasta %s has been added with output <%s> :thumbsup:" %(command, output))
            else:
                await self.bot.say("Copypasta %s has been added with output %s :thumbsup:"  % (command, output))
            print("Registered copypasta %s" %command)

    # Allowed the removal of a meme from the data file
    @checks.is_owner()
    @commands.command(hidden=True)
    async def delpasta(self, command: str):
        with open("copypastas.txt") as file:
            pasta = json.load(file)
            file.close()
        with open("copypastas.txt", "w") as file:
            if command in pasta:
                del pasta[command]
                save = json.dumps(pasta)
                file.write(save)
                await self.bot.say("Copypasta %s has been removed :thumbsup:" %command)
                print("Unregistered copypasta %s" %command)
            else:
                save = json.dumps(pasta)
                file.write(save)
                await self.bot.say("Copypasta not registered, could not delete :thumbsdown: ")
                print("Unregister copypasta error, no pasta %s" %command)

    # Lists all the memes currently stored
    # Command output looks really ugly
    # Needs make-over
    @commands.command()
    async def copypastas(self):
        """Lists the copypastas availible to output"""
        with open("copypastas.txt") as file:
            pasta = json.load(file)
            pastalist = "```Memes:"
            for x in pasta.keys():
                pastalist = "%s\n- %s" %(pastalist, x)
            await self.bot.say("%s```" %pastalist)
            print("Run: Copypastas Listed")

    # Allows the user to find and execute a meme
    @commands.command()
    async def pasta(self, input):
        """Outputs a selected copypasta"""
        with open("copypastas.txt") as file:
            pasta = json.load(file)
            if input in pasta:
                await self.bot.say(pasta[input])
                print("Run: Copypasta %s" %input)
            else:
                await self.bot.say("That's not a registered copypasta, pm bot owner to get it registered. :zzz: ")
                print("Unregistered copypasta %s executed" % input)


    #####################
    ## Random commands ##
    #####################

    # Random delet this image
    # Couldn't be bothered to write the meme comand to do random images for a meme
    # so this can stay separate
    @commands.command()
    async def deletthis(self):
        """Shows a random delet this image."""
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
        print("Run: Delete This")

    # Tells the @'d user to kill themselves
    # This is a special meme that requires input arguments
    # So also is not part of the meme command
    @commands.command(pass_context=True)
    async def kys(self, ctx, member: discord.Member = None):
        """Tells the mentioned user to kill themselves."""
        if member == None:
            member = ctx.message.author
        await self.bot.say("{0.mention} you should kill yourself".format(member))
        print("{0.name} told {1.name} to kill themselves".format(ctx.message.author, member))

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
        print("F to pay respects")

def setup(bot):
    bot.add_cog(Misc(bot))
