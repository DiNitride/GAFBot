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
        """Updates the Bot's status
        Usage:
        $status This is my status"""
        # Update the bots game
        await self.bot.change_status(discord.Game(name=status))
        await self.bot.say("Status updated to {}".format(status))
        print("Exec: Updated Bot's status to {}".format(status))

    # Lists bot's servers
    @commands.group(invoke_without_command=True)
    @commands.check(checks.is_owner)
    async def servers(self):
        """Commands for managing what servers the bot is part of
        Defaults to showing the server list"""
        list = []
        for x in self.bot.servers:
            list.append(x.name)
        await self.bot.say(list)
        print("Exec: Server list")

    # Makes the bot leave a server
    @servers.command()
    @commands.check(checks.is_owner)
    async def leave(self, *server: str):
        """Leaves a server the bot is in
        Usage:
        $leave The Never Ending GAF"""
        server = discord.utils.get(self.bot.servers, name=server)
        if server is None:
            await self.bot.say("No server found")
            return
        await self.bot.leave_server(server)
        print("Exec: Left Server {}".format(server.name))


    @servers.command()
    @commands.check(checks.is_owner)
    async def invite(self, *server: str):
        """Creates a server invite
        Usage:
        $invite The Never Ending GAF"""
        server = discord.utils.get(self.bot.servers, name=server)
        if server is None:
            await self.bot.say("No server found")
            return
        invite = await self.bot.create_invite(server)
        await self.bot.say(invite.url)

def setup(bot):
    bot.add_cog(Admin(bot))