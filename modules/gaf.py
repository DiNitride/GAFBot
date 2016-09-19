from discord.ext import commands

class GAF():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def GAF(self):
        """Information on The Never Ending GAF"""
        await self.bot.say("**What is GAF?**\nGAF is a small community/clan/group that reside on this Discord server to "
                           "engage in many diferent homoerotic autistic activities. We're not an organisation,"
                           "just a group of close friends that hang out and tell each other to kill ourselfs reguarly.\n\n"
                           "Simply put, GAF isn't a way of life, GAF is the lack of having a way of life.\n"
                           "Server Invite: https://discord.gg/tK4uQEU\n"
                           "Steam Page: <http://steamcommunity.com/groups/TheNeverEndingGAF>")

def setup(bot):
    bot.add_cog(GAF(bot))