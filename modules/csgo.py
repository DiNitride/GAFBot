import discord
from discord.ext import commands
import random

class CSGO():
    def __init__(self, bot):
        self.bot = bot
        self.maps = {"Cobblestone":"O","Dust 2":"O"}
        self.mapnames = {"cobblestone":"Cobblestone","dust2":"Dust 2"}
        self.veto_bool = False

    @commands.command(pass_context=True)
    async def veto(self, ctx, map):
        #Is there a veto running
        if self.veto_bool:
            #Is it their turn
            if ctx.message.author is self.turn:
                map = map.lower()
                vetocheck = []
                #Idk what this is for tbh it's just here
                for x in self.maps:
                    vetocheck.append(x)
                maplist = "\n- ".join(self.mapnames.values())
                #Does the map exist
                if map.lower() in self.maps.lower():
                    #Has it been veto-ed
                    if self.maps[map] == 'X':
                        await self.bot.say("That map has already been veto-ed.")
                    else:
                        #Veto the map
                        self.maps[map] = 'X'
                        await self.bot.say("{0} has been veto-ed.".format(self.mapnames[map]))
                        await self.bot.say("**Availible maps:**\n- {0}".format(maplist))
                else:
                    #Map no exist
                    await self.bot.say("Please select a map that exists.")
            else:
                await self.bot.say("Please wait your turn, it is {0}'s turn".format(self.turn.mention))
        else:
            await self.bot.say("Please start a veto with !startveto.")

    @commands.command(pass_context=True)
    async def startveto(self, ctx, a: discord.User, b: discord.User):
        self.user1 = a
        self.user2 = b
        self.turn = self.user1
        if not self.veto_bool:
            author = ctx.message.author
            maplist = '\n- '.join(self.mapnames.values())
            await self.bot.say("Starting veto...")
            self.vetoadmin = author.id
            self.veto_bool = True
            await self.bot.say("Veto Begun!")
            await self.bot.say("**Availible maps:**\n- {0}".format(maplist))
            await self.bot.say("It is {0}'s turn".format(self.user1.mention))
        else:
            await self.bot.say("Please wait for the current veto to finish")

    @commands.command(pass_context=True)
    async def endveto(self, ctx):
        if self.veto_bool:
            author = ctx.message.author
            is_mod = any((role.permissions.administrator or role.permissions.kick_members or role.permissions.manage_messages) for role in ctx.message.author.roles)
            if author.id is self.vetoadmin:
                vetoadmin = True
            if vetoadmin or is_mod:
                await self.bot.say("Ending veto...")
                self.veto_bool = False
                await self.bot.say("Veto ended.")
            else:
                await self.bot.say("You do not have permission to end the current veto")
        else:
            await self.bot.say("There is not veto currently in progress")

    @commands.command()
    async def vetomaps(self):
        maplist = '\n- '.join(self.mapnames)
        await self.bot.say("**Availible maps:**\n- {0}".format(maplist))

def setup(bot):
    bot.add_cog(CSGO(bot))
