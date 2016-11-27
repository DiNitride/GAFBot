import discord
from discord.ext import commands
import asyncio
from utils import checks

class Prank():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(checks.is_owner)
    async def lol(self, ctx):
        server = ctx.message.server
        await self.bot.delete_message(ctx.message)
        while True:
            await self.bot.create_channel(server, 'Sam is a twat', type=discord.ChannelType.voice)
            await asyncio.sleep(5)



def setup(bot):
    bot.add_cog(Prank(bot))
