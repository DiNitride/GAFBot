from discord.ext import commands
import discord
import json
import asyncio
from utils import logging

log = logging.Logging

with open("config/server_setting_defaults.json") as data:
    default = json.load(data)

class Settings:

    def __init__(self):
        with open("config/serversettings.json") as data:
            self.settings = json.load(data)

        asyncio.Task(self.save())

    # Checks if the server has a config file
    # Makes one if not
    def check(self, server):
        if server.id in self.settings:
            return True
        else:

            try:
                self.settings[server.id] = default
                return True
            except Exception():
                return False

    # Retrieves the value of an option from the config
    def retrieve(self, server: discord.Server, option: str):
        if self.check(server):
            try:
                out = self.settings[server.id][option]
            except KeyError:
                try:
                    self.settings[server.id][option] = default[option]
                except KeyError:
                    return False
                out = self.settings[server.id][option]
            return out

    # Edits the value of an option in config
    def edit(self, server: discord.Server, option: str, new):
        if self.check(server):
            self.settings[server.id][option] = new
            return True

    async def save(self):
        while True:
            await asyncio.sleep(60)
            save = json.dumps(self.settings)
            with open("config/serversettings.json", "w") as data:
                data.write(save)
            logging.log("[SYSTEM]", "Saved Server Config to file")

