import discord
from discord.ext import commands
from utils import checks

class Subscriptions():
    def __init__(self, bot):
        self.bot = bot

        # Options for different gams
        # ID first entry
        # Pretty, correctly spelt name as last
        # Various ways of inputting in the middle
        self.csgooptions = ['186030599394295808', "cs", "csgo", "cs:go", "CS:GO"]
        self.owoptions = ['243852225300922369', "ow", "overwatch", "Overwatch"]
        self.archageoptions = ['243851872262160384', "aa", "archage", "Archeage"]
        self.diablooptions = ['239751503877767168', "diablo", "d3", "Diablo III"]
        self.rustoptions = ['221901793246969857', 'rust', 'Rust']

        self.allOptions = [self.csgooptions, self.owoptions, self.archageoptions, self.diablooptions, self.rustoptions]

        # Creates a string of availible games to Subscribe to
        listStr = ""
        for x in self.allOptions:
            listStr = listStr + ("\n" + x[-1])
        # Makes that string look pretty
        self.avgames = "```Games availible to subscribe to: %s ```" % listStr

        # Lists the avalible games to subscribe to

    @checks.is_gaf_server()
    @commands.command()
    async def games(self):
        """Lists avalible games to subscribe to"""
        await self.bot.say(self.avgames)
        print("Run: Games List")

    @checks.is_gaf_server()
    @commands.command(pass_context=True)
    async def subscribe(self, ctx, game: str):
        """Subscribes you to game notifications"""
        server = ctx.message.server
        member = ctx.message.author
        self.sub = True
        valid = False
        for options in self.allOptions:
            if game.lower() in options:
                role = discord.utils.get(server.roles, id=options[0])
                await self.bot.add_roles(member, role)
                await self.bot.say(
                    "%s your notification settings for %s are now %s" % (member.mention, options[-1], self.sub))
                print("%s your notification settings for %s are now %s" % (member.name, options[-1], self.sub))
                valid = True
                break
        if not valid:
            await self.bot.say(self.avgames)

    @checks.is_gaf_server()
    @commands.command(pass_context=True)
    async def unsubscribe(self, ctx, game: str):
        """Unsubscribes you from a games notifications"""
        server = ctx.message.server
        member = ctx.message.author
        self.sub = False
        valid = False
        for options in self.allOptions:
            if game.lower() in options:
                role = discord.utils.get(server.roles, id=options[0])
                await self.bot.remove_roles(member, role)
                await self.bot.say(
                    "%s your notification settings for %s are now %s" % (member.mention, options[-1], self.sub))
                print("%s your notification settings for %s are now %s" % (member.name, options[-1], self.sub))
                valid = True
                break
        if not valid:
            await self.bot.say(self.avgames)

    # # Lists the users game subscriptions
    # @checks.is_gaf_server()
    # @commands.command(pass_context=True)
    # async def subscriptions(self, ctx):
    #     """Lists your game subscriptions"""
    #     server = ctx.message.server
    #     member = ctx.message.author
    #     shn = False
    #     csn = False
    #     own = False
    #     psn = False
    #     inn = False
    #     gvn = False
    #     pun = False
    #     for x in member.roles:
    #         role = discord.utils.get(server.roles, id=self.shoptions[0])
    #         if x == role:
    #             shn = True
    #         role = discord.utils.get(server.roles, id=self.csgooptions[0])
    #         if x == role:
    #             csn = True
    #         role = discord.utils.get(server.roles, id=self.owoptions[0])
    #         if x == role:
    #             own = True
    #         role = discord.utils.get(server.roles, id=self.psoptions[0])
    #         if x == role:
    #             psn = True
    #         role = discord.utils.get(server.roles, id=self.inoptions[0])
    #         if x == role:
    #             inn = True
    #         role = discord.utils.get(server.roles, id=self.gtaoptions[0])
    #         if x == role:
    #             gvn = True
    #         role = discord.utils.get(server.roles, id=self.poption[0])
    #         if x == role:
    #             pun = True
    #     await self.bot.say(
    #         "Your notification settings are:\nTabletop Simulator: {0}\nCS:GO: {1}\nOverwatch: {2}\nPlanetside 2: {3}\nInsurgency: {4}\nGTA V: {5}\nPulsar: {6}".format(
    #             shn, csn, own, psn, inn, gvn, pun))
    #     print("Printed {0.name}'s notifcation settings".format(member))

def setup(bot):
    bot.add_cog(Subscriptions(bot))
