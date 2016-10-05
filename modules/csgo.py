import discord
from discord.ext import commands
import random
import asyncio
import xml.etree.ElementTree as ET
from urllib import request
from utils import net

class CSGO():
    def __init__(self, bot):
        self.bot = bot
        self.instances = []

    @commands.command(pass_context=True)
    async def veto(self, ctx, user_1: discord.User = None, user_2: discord.User = None):
        """Starts a CS:GO map veto. Uses the current active duty maps
        Usage:
        $veto @TeamLeader1 @TeamLeader2"""

        channel = ctx.message.channel
        author = ctx.message.channel

        if user_1 is None or user_2 is None:
            await self.bot.say("Please specify the 2 team captains in the veto by mentioning them.\nE.g. $veto @captainA @captainB")
            return

        if author.id in self.instances:
            await self.bot.say("Please wait for your current veto to finish.")
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

        await self.bot.say("CS:GO Map Veto Started")

        await self.bot.say("Picking who picks first...")
        first = random.randint(0,1)
        if first is 0:
            turn = user_1
        else:
            turn = user_2
        await asyncio.sleep(1)
        await self.bot.say("{0.mention} is picking first!".format(turn))

        while True:

            await self.bot.say("{0.mention}'s pick".format(turn))

            rotation = ""
            for x in maps:
                if maps[x]["status"] is 1:
                    vetoed = " : :no_entry_sign:"
                else:
                    vetoed = " "
                rotation = rotation + "- " + maps[x]["name"] + vetoed + "\n"

            await self.bot.say("Maps in rotation:\n{0}\nWhat map would you like to veto? ('quit' to exit)".format(rotation))

            picked = False
            error_count = 0

            while picked is False:
                if error_count is 4:
                    await self.bot.say("Too many incorrect vetos, cancelling veto.")
                    self.instances.remove(author.id)
                    return

                veto = await self.bot.wait_for_message(timeout=180, author=turn or author, channel=channel)

                if veto is None:
                    await self.bot.say("Took too long to respond, cancelling veto.")
                    self.instances.remove(author.id)
                    return

                if veto == "quit":
                    await self.bot.say("Cancelling veto...")
                    await self.bot.say("Veto cancelled")
                    self.instances.remove(author.id)
                    return

                for x in maps:
                    if veto.content.lower() in maps[x]["inputs"]:
                        if maps[x]["status"] is 1:
                            await self.bot.say("That map has been veto-ed, please pick again")
                            error_count += 1
                            break
                        veto = maps[x]
                        picked = True
                        break

            await self.bot.say("Veto {0}".format(veto["name"]))
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

        await self.bot.say("Map Veto Over!\n{0}\nMap {1} has been picked!\n".format(rotation, choice))
        self.instances.remove(author.id)

    @commands.command()
    async def csgostats(self, id):
        """Player stats for Counter Strike: Global Offensive. ID must be Steam ID or Vanity ID
        Usage:
        $csgostats dinitride"""
        api_url = "http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={0}&steamid={1}"
        xml_url = "http://steamcommunity.com/id/{0}/?xml=1"
        steam_api_key = self.bot.config["api_keys"]["steam"]

        response, stats, status = await net.get_url(api_url.format(steam_api_key, id), {"user-agent" : "GAF Bot"})

        if status == 400:
            xml_str = request.urlopen(xml_url.format(id)).read()
            root = ET.fromstring(xml_str)
            id = root.find('steamID64').text

        elif status == 504:
            await self.bot.say("Server error")
            return

        response, stats, status = await net.get_url(api_url.format(steam_api_key, id), {"user-agent" : "GAF Bot"})

        for entry in range(len(stats["playerstats"]["stats"])):
            if stats["playerstats"]["stats"][entry]["name"] == "total_kills":
                total_kills = stats["playerstats"]["stats"][entry]["value"]
            if stats["playerstats"]["stats"][entry]["name"] == "total_deaths":
                total_deaths = stats["playerstats"]["stats"][entry]["value"]
            if stats["playerstats"]["stats"][entry]["name"] == "total_time_played":
                total_time_played = stats["playerstats"]["stats"][entry]["value"]
            if stats["playerstats"]["stats"][entry]["name"] == "total_planted_bombs":
                total_planted_bombs = stats["playerstats"]["stats"][entry]["value"]
            if stats["playerstats"]["stats"][entry]["name"] == "total_money_earned":
                total_money_earned = stats["playerstats"]["stats"][entry]["value"]
            if stats["playerstats"]["stats"][entry]["name"]  == "total_kills_knife":
                total_kills_knife = stats["playerstats"]["stats"][entry]["value"]
            if stats["playerstats"]["stats"][entry]["name"] == "last_match_kills":
                last_match_kills = stats["playerstats"]["stats"][entry]["value"]
            if stats["playerstats"]["stats"][entry]["name"] == "last_match_deaths":
                last_match_deaths = stats["playerstats"]["stats"][entry]["value"]
            if stats["playerstats"]["stats"][entry]["name"] == "total_mvps":
                total_mvps = stats["playerstats"]["stats"][entry]["value"]
            if stats["playerstats"]["stats"][entry]["name"] == "total_matches_won":
                total_matches_won = stats["playerstats"]["stats"][entry]["value"]

        await self.bot.say("""```xl\nTotal Kills: {0}\nTotal Deaths: {1}\nKills/Deaths: {2}\nPlaytime: {3} hours\nTotal Bombs Planted: {4}\nTotal Money Earned: {5}\nTotal MVPs: {6}\nTotal Knife Kills: {7}\nTotal Matches Won: {8}\nLast Match Stats:\nKills: {9}\nDeaths: {10}\n```""".format(total_kills, total_deaths, total_kills/total_deaths, int(total_time_played/60/60), total_planted_bombs, total_money_earned, total_mvps, total_kills_knife, total_matches_won, last_match_kills, last_match_deaths))

def setup(bot):
    bot.add_cog(CSGO(bot))
