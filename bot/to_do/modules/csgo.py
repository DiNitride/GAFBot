import random
import asyncio

import discord
from discord.ext import commands

from utils import reaction_menu


class CSGO():

    def __init__(self, bot):
        self.bot = bot
        self.instances = []

    @commands.command()
    async def veto(self, ctx, user_1: discord.User = None, user_2: discord.User = None):
        """Starts a CS:GO map veto. Uses the current active duty maps"""

        channel = ctx.message.channel
        author = ctx.message.channel

        if user_1 is None or user_2 is None:
            await ctx.send("Please specify team captains")
            return

        if author.id in self.instances:
            await ctx.send("Please wait for your current veto to finish.")
            return

        self.instances.append(author.id)

        maps = {
            "de_dust2" : { "name" : "Dust 2", "status" : 0,
                           "inputs" : ["de_dust2", "dust2", "dust 2"]},
            "de_cbble" : { "name" : "Cobblestone", "status" : 0,
                           "inputs" : ["de_cbble", "cobble", "cobblestone"]},
            "de_nuke" : { "name" : "Nuke", "status" : 0,
                          "inputs": ["de_nuke", "nuke"]},
            "de_mirage" : { "name" : "Mirage", "status" : 0,
                            "inputs": ["de_mirage", "mirage"]},
            "de_cache" : { "name" : "Cache", "status" : 0,
                           "inputs": ["de_cache", "cache"]},
            "de_train" : { "name" : "Train", "status" : 0,
                           "inputs": ["de_train", "train"]},
            "de_overpass" : {"name" : "Overpass", "status" : 0,
                             "inputs": ["de_overpass", "overpass"]}
        }

        await ctx.send("CS:GO Map Veto Started")

        await ctx.send("Picking who picks first...")
        first = random.randint(0,1)
        if first is 0:
            turn = user_1
        else:
            turn = user_2
        await asyncio.sleep(1)
        await ctx.send("{0.mention} is picking first!".format(turn))

        while True:

            await ctx.send("{0.mention}'s pick".format(turn))

            rotation = ""
            for x in maps:
                if maps[x]["status"] is 1:
                    vetoed = " : :no_entry_sign:"
                else:
                    vetoed = " "
                rotation = rotation + "- " + maps[x]["name"] + vetoed + "\n"

            await ctx.send("Maps in rotation:\n{0}\nWhat map would you like to veto? ('quit' to exit)".format(rotation))

            picked = False
            error_count = 0

            while picked is False:
                if error_count is 4:
                    await ctx.send("Too many incorrect vetos, cancelling veto.")
                    self.instances.remove(author.id)
                    return

                veto = await self.bot.wait_for_message(timeout=180, author=turn or author, channel=channel)

                if veto is None:
                    await ctx.send("Took too long to respond, cancelling veto.")
                    self.instances.remove(author.id)
                    return

                if veto.content == "quit":
                    await ctx.send("Cancelling veto...")
                    await ctx.send("Veto cancelled")
                    self.instances.remove(author.id)
                    return

                for x in maps:
                    if veto.content.lower() in maps[x]["inputs"]:
                        if maps[x]["status"] is 1:
                            await ctx.send("That map has been veto-ed, please pick again")
                            error_count += 1
                            break
                        veto = maps[x]
                        picked = True
                        break

            await ctx.send("Veto {0}".format(veto["name"]))
            maps[x]["status"] = 1

            done = 0
            for x in maps:
                if maps[x]["status"] is 0:
                    done += 1

            if done is 1:
                break

            if turn is user_1:
                turn = user_2
            else:
                turn = user_1

        for x in maps:
            if maps[x]["status"] is 0:
                choice = maps[x]["name"]

        rotation = ""
        for x in maps:
            if maps[x]["status"] is 1:
                vetoed = " : :no_entry_sign:"
            else:
                vetoed = " : :white_check_mark:"
            rotation = rotation + "- " + maps[x]["name"] + vetoed + "\n"

        await ctx.send("Map Veto Over!\n{0}\nMap {1} has been picked!\n".format(rotation, choice))
        self.instances.remove(author.id)


def setup(bot):
    bot.add_cog(CSGO(bot))
