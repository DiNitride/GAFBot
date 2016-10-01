import discord
from discord.ext import commands
import json
from utils import checks
from utils import setting

class Config():
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def config(self):
        """Offers server config commands"""


    @config.command(pass_context=True)
    @commands.check(checks.is_admin)
    async def logging(self, ctx):
        """Turns logging on or off in the desired channel
        Logging may only be active in one channel per sever"""

        server = ctx.message.server
        channel = ctx.message.channel

        if self.bot.settings.retrieve(server, "logging"):
            self.bot.settings.edit(server, "logging", False)
            self.bot.settings.edit(server, "log_channel", "")
            await self.bot.say("Logging disabled for **{0}**".format(server.name))
            return

        else:
            self.bot.settings.edit(server, "logging", True)
            self.bot.settings.edit(server, "log_channel", channel.id)
            await self.bot.say("Logging set to **{0}** in channel **{1}** for **{2}**:pencil: "
                               .format(setting.retrieve(server, "logging"), channel.name, server.name))
            return

    @config.command(pass_context=True)
    @commands.check(checks.is_admin)
    async def join_role(self, ctx, role: str = None):
        """Turns the role on join system on and selects role
        e.g. $join_role Guest
        Will grant the role Guest to users as they join
        To disable:
        $join_role False"""

        server = ctx.message.server

        if role.lower() == "false":
            self.bot.settings.edit(server, "role_on_join", False)
            await self.bot.say("Role on join disabled for {0.name} :pencil:".format(server))
            return

        # Search for role
        role = discord.utils.find(lambda m: m.name == role, server.roles)
        # Return if nothing is found
        if role is None:
            await self.bot.say("No role found.\n(This is case sensitive, it may help if you @mention the role)")
            return
        else:
            self.bot.settings.edit(server, "role_on_join", True)
            self.bot.settings.edit(server, "join_role", role.id)
            await self.bot.say("Role {0.name} will be granted to users as they join {1.name}".format(role, server))
            return

def setup(bot):
    bot.add_cog(Config(bot))