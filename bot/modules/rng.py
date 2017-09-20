import re
import random

import discord
from discord.ext import commands


class RNG:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dice(self, ctx, dice: str):
        """
        Rolls a dice in NdN format.
        """
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format has to be in NdN!')
            return

        if (rolls or limit) > 100:
            await ctx.send("Go away Profound. `(Size too big)`")
        else:
            result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
            await ctx.send(result)

    @commands.command()
    async def choose(self, ctx, *choices: str):
        """
        Chooses between multiple choices, surround choices with spaces in quotes.
        """
        await ctx.send(f"I choose: {re.sub('@here', '', re.sub('@everyone', '', random.choice(choices)))}")


def setup(bot):
    bot.add_cog(RNG(bot))
