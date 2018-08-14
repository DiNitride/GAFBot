from datetime import datetime as dt

import discord
from discord.ext import commands
from dinnerplate import BaseCog, JsonConfigManager

DEFAULT = {
    "guild_id": None,
    "guild": None,
    "commands": None
}


class BotLogging(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)
        self.config = JsonConfigManager("bot_logging.json", DEFAULT)

    def get_guild(self):
        return discord.utils.get(self.bot.guilds, id=self.config["guild_id"])

    @staticmethod
    def construct__guild_message(msg_type, guild):
        return f"```\n" \
               f"{dt.now()} --- {msg_type} GUILD\n" \
               f"Guild: {guild.name} -- {guild.id}\n" \
               f"Owner: {guild.owner} -- {guild.owner.id}\n" \
               f"```"

    async def on_guild_join(self, guild):
        msg_guild = self.get_guild()
        channel = msg_guild.get_channel(self.config["guild"])
        await channel.send(BotLogging.construct__guild_message("JOINED", guild))

    async def on_guild_remove(self, guild):
        msg_guild = self.get_guild()
        channel = msg_guild.get_channel(self.config["guild"])
        await channel.send(BotLogging.construct__guild_message("LEFT", guild))

    async def on_command(self, ctx):
        msg_guild = self.get_guild()
        channel = msg_guild.get_channel(self.config["commands"])
        await channel.send(f"```\n"
                           f"{dt.now()} --- COMMAND CALLED\n"
                           f"Command: '{ctx.command}'\n"
                           f"Args: {ctx.args}\n"
                           f"Parameters: {ctx.kwargs}\n"
                           f"Invoker: {ctx.author} -- {ctx.author.id}\n"
                           f"Failed?: {ctx.command_failed}\n"
                           f"Channel: {ctx.channel} -- {ctx.channel.id}\n"
                           f"Guild: {ctx.guild.name} -- {ctx.guild.id}\n"
                           f"```")


setup = BotLogging.setup
