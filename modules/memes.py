import discord
from discord.ext import commands
import random

class Memes():
    def __init__(self, bot):
        self.bot = bot

    # Example Command for me to copy and paste BC I'm lazy
    # @commands.command()
    # async def command(self):
    #     """Command Description"""
    #     await self.bot.say("Command")
    #     print("Run: Command")

    # Noided
    @commands.command()
    async def noided(self):
        """Shows Noided image."""
        await self.bot.say("http://i.imgur.com/Q2nGkFB.png")
        print("Run: Noided")

    # Random delet this image
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

    # Prints a random amount of white emojiss
    @commands.command()
    async def funny(self, times : int):
        """Prints random white emoji's a certain amount of times."""
        emoji=[":joy:" , ":ok_hand:"]
        msg = ""
        for x in range(times):
            msg += random.choice(emoji)
        await self.bot.say(msg)
        print("Run: Funny White Girl Hands")

    # Idk it's an image of an african slapping a liquid with a sandal ask Cam
    @commands.command()
    async def bpoil(self):
        """Real life footage of the BP oil spill"""
        await self.bot.say("http://i.imgur.com/OR5LMud.gif")
        print("Run: bpoil")

    #Shows an image of how the twin towers fell
    @commands.command()
    async def howbushdidit(self):
        """How did Bush do 9/11? We have answers."""
        await self.bot.say("http://i.imgur.com/v19J7fP.gif")
        print("Run: howbushdidit")

    # Displays the chemical formula for bleach
    @commands.command()
    async def bleach(self):
        """"Have you ever thought about making your own bleach?"""
        await self.bot.say("2NaOH + Cl2 -> NaCl +NaClO +H2O")
        print("Run: Bleach Formuala")

    # Tells the @'d user to kill themselves
    @commands.command(pass_context=True)
    async def kys(self, ctx, member: discord.Member = None):
        """Tells the mentioned user to kill themselves."""
        if member == None:
            member = ctx.message.author
        await self.bot.say("{0.mention} you should kill yourself".format(member))
        print("{0.name} told {1.name} to kill themselves".format(ctx.message.author, member))

    # F to pay resepects
    @commands.command()
    async def f(self):
        """Pay respects"""
        await self.bot.say("Respect")
        print("F to pay respects")

def setup(bot):
    bot.add_cog(Memes(bot))
