import discord
from discord.ext import commands
from utils import checks
import json

class Admin():
    def __init__(self, bot):
        self.bot = bot

    # Changes the bot's game
    @commands.command(pass_conext=True)
    @commands.check(checks.is_owner)
    async def status(self, *, status: str):
        """Updates the Bot's status"""

        # Update the bots game
        await self.bot.change_status(discord.Game(name=status))

        # Saves status to config
        with open("config/variables.json") as data:
            varb = json.load(data)
            varb["status"] = status
        with open("config/variables.json", "w") as edit:
            save = json.dumps(varb)
            edit.write(save)

        # Outputs
        await self.bot.say("Status updated to {}".format(status))
        print("Updated Bot's status to {}".format(status))

def setup(bot):
    bot.add_cog(Admin(bot))
