import discord
from discord.ext import commands
from utils import checks

class Admin():
    def __init__(self, bot):
        self.bot = bot

    # Changes the bot's game
    @commands.command(pass_conext=True)
    @commands.check(checks.is_owner)
    async def changegame(self, *, game: str):
        """Updates the Bot's game"""
        # Update the bots game
        await self.bot.change_status(discord.Game(name=game))
        await self.bot.say("Game updated.")
        print("Updated Bot's Game")

def setup(bot):
    bot.add_cog(Admin(bot))
