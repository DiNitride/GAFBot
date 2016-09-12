import discord
from discord.ext import commands
import json
from utils import checks
from utils import setting

class Config():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(checks.is_admin)
    async def logging(self, ctx):
        server = ctx.message.server
        if not setting.is_in_data(ctx.message):
            await bot.say("Failed to initialise server file")
            return
        with open("config/serversettings.json") as file:
            data = json.load(file)
            if data[server.id]["logging"] is True:
                data[server.id]["logging"] = False
            elif data[server.id]["logging"] is False:
                data[server.id]["logging"] = True
                data[server.id]["log_channel"] = ctx.message.channel.id
            with open("config/serversettings.json", "w") as file:
                save = json.dumps(data)
                file.write(save)
            await self.bot.say("Logging set to **{0}** in channel **{1}** :pencil: ".format(data[server.id]["logging"],ctx.message.channel.name))

    @commands.command(pass_context=True)
    @commands.check(checks.is_admin)
    async def join_role_off(self, ctx):
        server = ctx.message.server
        if not setting.is_in_data(ctx.message):
            await bot.say("Failed to initialise server file")
            return
        with open("config/serversettings.json") as file:
            data = json.load(file)
            data[server.id]["role_on_join"] = False
            with open("config/serversettings.json", "w") as file:
                save = json.dumps(data)
                file.write(save)
            await self.bot.say("Role on join disabled for {0.name} :pencil:".format(server))

    @commands.command(pass_context=True)
    @commands.check(checks.is_admin)
    async def join_role(self, ctx, role):
        server = ctx.message.server
        if not setting.is_in_data(ctx.message):
            await bot.say("Failed to initialise server file")
            return
        with open("config/serversettings.json") as file:
            data = json.load(file)
            data[server.id]["role_on_join"] = True
            role = discord.utils.find(lambda m: m.name == role, server.roles)
            if role is None:
                await self.bot.say("No role found.")
                return
            else:
                data[server.id]["join_role"] = role.id
                with open("config/serversettings.json", "w") as file:
                    save = json.dumps(data)
                    file.write(save)
                await self.bot.say("Role {0.name} will be granted to users as they join {1.name}".format(role, server))

def setup(bot):
    bot.add_cog(Config(bot))