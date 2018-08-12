from datetime import datetime as dt

import discord
from discord.ext import commands
from dinnerplate import BaseCog, JsonConfigManager

DEFAULT = {
    "guild_id": None,
    "guild": None
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


setup = BotLogging.setup
