import discord
from discord.ext import commands
import json
from utils import net

class Overwatch():
    def __init__(self, bot):
        self.bot = bot
        self.instances = []


    @commands.command()
    async def owavgstats(self, battlenet):
        """Average player stats for an Overwatch user
        Usage:
        $owavgstats DiNitride#2961"""
        api_url = "https://owapi.net/api/v2/u/{0}/stats/general"
        battlenet_for_api = battlenet.replace("#","-")

        response, stats, status = await net.get_url(api_url.format(battlenet_for_api), {"user-agent" : "GAF Bot"})

        if status == 404:
            await self.bot.say("Error: User has no competitive stats, or Battle.net was entered incorrectly")
            return

        elif status == 504:
            await self.bot.say("Server error")
            return

        damage_done_avg = stats["average_stats"]["damage_done_avg"]
        deaths_avg = stats["average_stats"]["deaths_avg"]
        eliminations_avg = stats["average_stats"]["eliminations_avg"]
        final_blows_avg = stats["average_stats"]["final_blows_avg"]
        healing_done_avg = stats["average_stats"]["healing_done_avg"]
        objective_kills_avg = stats["average_stats"]["objective_kills_avg"]
        objective_time_avg = stats["average_stats"]["objective_time_avg"]
        solo_kills_avg = stats["average_stats"]["solo_kills_avg"]
        time_spent_on_fire_avg = stats["average_stats"]["time_spent_on_fire_avg"]

        await self.bot.say("```xl\n"
                           "Average Stats for {0}\n"
                           "Damage Done: {1}\n"
                           "Deaths: {2}\n"
                           "Eliminations: {3}\n"
                           "Final Blows: {4}\n"
                           "Objective Kills: {5}\n"
                           "Objective Time: {6}\n"
                           "Solo Kills: {7}\n"
                           "Time spent of fire: {8}\n"
                           "```".format(battlenet, damage_done_avg, deaths_avg, eliminations_avg, final_blows_avg,
                                        healing_done_avg, objective_kills_avg, objective_time_avg, solo_kills_avg,
                                        time_spent_on_fire_avg))

    @commands.command()
    async def owstats(self, battlenet):
        """Player stats for an Overwatch user
        Usage:
        $owstats DiNitride#2961"""
        api_url = "https://owapi.net/api/v2/u/{0}/stats/general"
        battlenet_for_api = battlenet.replace("#", "-")

        response, stats, status = await net.get_url(api_url.format(battlenet_for_api), {"user-agent" : "GAF Bot"})

        if status == 404:
            await self.bot.say("Error: User has no competitive stats, or Battle.net was entered incorrectly")
            return

        elif status == 504:
            await self.bot.say("Server error")
            return

        damage_done = stats["game_stats"]["damage_done"]
        deaths = stats["game_stats"]["deaths"]
        eliminations = stats["game_stats"]["eliminations"]
        environmental_deaths = stats["game_stats"]["environmental_deaths"]
        environmental_kill = stats["game_stats"]["environmental_kill"]
        final_blows = stats["game_stats"]["final_blows"]
        games_won = stats["game_stats"]["games_won"]
        healing_done = stats["game_stats"]["healing_done"]
        kpd = stats["game_stats"]["kpd"]
        medals = stats["game_stats"]["medals"]
        medals_bronze = stats["game_stats"]["medals_bronze"]
        medals_gold = stats["game_stats"]["medals_gold"]
        medals_silver = stats["game_stats"]["medals_silver"]
        objective_kills = stats["game_stats"]["objective_kills"]
        objective_time = stats["game_stats"]["objective_time"]
        solo_kills = stats["game_stats"]["solo_kills"]
        time_played = stats["game_stats"]["time_played"]

        await self.bot.say("```xl\n"
                           "Stats for {0}\n"
                           "Damage Done: {1}\n"
                           "Eliminations: {2}\n"
                           "Final Blows: {3}\n"
                           "Multikills: {4}\n"
                           "Solo Kills: {5}\n"
                           "Deaths: {6}\n"
                           "Kills to Deaths: {7}\n"
                           "Environmental Deaths: {8}\n"
                           "Healing Done: {9}\n"
                           "Medals:\n"
                           "Total: {10}\n"
                           "Gold: {11}\n"
                           "Silver: {12}\n"
                           "Bronze: {13}\n"
                           "Objective Kills: {14}\n"
                           "Objective Time: {15}\n"
                           "Time Played: {16}\n"
                           "Games Won: {17}\n"
                           "```".format(battlenet, damage_done, eliminations, final_blows,
                                                    solo_kills, deaths, kpd, environmental_deaths, environmental_kill,
                                                    healing_done, medals, medals_gold, medals_silver, medals_bronze,
                                                    objective_kills, objective_time, time_played, games_won))

    @commands.command()
    async def owcompavgstats(self, battlenet):
        """Average competitive player stats for an Overwatch user
        User must have played at least 1 competitive game
        Usage:
        $owcompavgstats DiNitride#2961"""
        api_url = "https://owapi.net/api/v2/u/{0}/stats/competitive"
        battlenet_for_api = battlenet.replace("#", "-")

        response, stats, status = await net.get_url(api_url.format(battlenet_for_api), {"user-agent" : "GAF Bot"})

        if status == 404:
            await self.bot.say("Error: User has no competitive stats, or Battle.net was entered incorrectly")
            return

        elif status == 504:
            await self.bot.say("Server error")
            return

        damage_done_avg = stats["average_stats"]["damage_done_avg"]
        deaths_avg = stats["average_stats"]["deaths_avg"]
        eliminations_avg = stats["average_stats"]["eliminations_avg"]
        final_blows_avg = stats["average_stats"]["final_blows_avg"]
        healing_done_avg = stats["average_stats"]["healing_done_avg"]
        objective_kills_avg = stats["average_stats"]["objective_kills_avg"]
        objective_time_avg = stats["average_stats"]["objective_time_avg"]
        solo_kills_avg = stats["average_stats"]["solo_kills_avg"]
        time_spent_on_fire_avg = stats["average_stats"]["time_spent_on_fire_avg"]

        await self.bot.say("```xl\n"
                           "Average Stats for {0}\n"
                           "Damage Done: {1}\n"
                           "Deaths: {2}\n"
                           "Eliminations: {3}\n"
                           "Final Blows: {4}\n"
                           "Objective Kills: {5}\n"
                           "Objective Time: {6}\n"
                           "Solo Kills: {7}\n"
                           "Time spent of fire: {8}\n"
                           "```".format(battlenet, damage_done_avg, deaths_avg, eliminations_avg, final_blows_avg,
                                        healing_done_avg, objective_kills_avg, objective_time_avg, solo_kills_avg,
                                        time_spent_on_fire_avg))

    @commands.command()
    async def owcompstats(self, battlenet):
        """Competitive player stats for an Overwatch user
        User must have played at least 1 competitive game
        Usage:
        $owcompstats DiNitride#2961"""
        api_url = "https://owapi.net/api/v2/u/{0}/stats/competitive"
        battlenet_for_api = battlenet.replace("#", "-")

        response, stats, status = await net.get_url(api_url.format(battlenet_for_api), {"user-agent" : "GAF Bot"})

        if status == 404:
            await self.bot.say("Error: User has no competitive stats, or Battle.net was entered incorrectly")
            return

        elif status == 504:
            await self.bot.say("Server error")
            return

        damage_done = stats["game_stats"]["damage_done"]
        deaths = stats["game_stats"]["deaths"]
        eliminations = stats["game_stats"]["eliminations"]
        environmental_deaths = stats["game_stats"]["environmental_deaths"]
        environmental_kill = stats["game_stats"]["environmental_kill"]
        final_blows = stats["game_stats"]["final_blows"]
        games_won = stats["game_stats"]["games_won"]
        healing_done = stats["game_stats"]["healing_done"]
        kpd = stats["game_stats"]["kpd"]
        medals = stats["game_stats"]["medals"]
        medals_bronze = stats["game_stats"]["medals_bronze"]
        medals_gold = stats["game_stats"]["medals_gold"]
        medals_silver = stats["game_stats"]["medals_silver"]
        objective_kills = stats["game_stats"]["objective_kills"]
        objective_time = stats["game_stats"]["objective_time"]
        solo_kills = stats["game_stats"]["solo_kills"]
        time_played = stats["game_stats"]["time_played"]

        await self.bot.say("```xl\n"
                           "Stats for {0}\n"
                           "Damage Done: {1}\n"
                           "Eliminations: {2}\n"
                           "Final Blows: {3}\n"
                           "Solo Kills: {4}\n"
                           "Deaths: {5}\n"
                           "Kills to Deaths: {6}\n"
                           "Environmental Deaths: {7}\n"
                           "Enviromental Kills: {8}\n"
                           "Healing Done: {9}\n"
                           "Medals:\n"
                           "Total: {10}\n"
                           "Gold: {11}\n"
                           "Silver: {12}\n"
                           "Bronze: {13}\n"
                           "Objective Kills: {14}\n"
                           "Objective Time: {15}\n"
                           "Time Played: {16}\n"
                           "Games Won: {17}\n"
                           "```".format(battlenet, damage_done, eliminations, final_blows,
                                        solo_kills, deaths, kpd, environmental_deaths, environmental_kill,
                                        healing_done, medals, medals_gold, medals_silver, medals_bronze,
                                        objective_kills, objective_time, time_played, games_won))

def setup(bot):
    bot.add_cog(Overwatch(bot))