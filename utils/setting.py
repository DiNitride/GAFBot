from discord.ext import commands
import discord
import json

with open("config/defaults.json") as data:
    default = json.load(data)

config = "config/serversettings.json"

# Checks if the server has a config file
# Makes one if not
def check(server):
    with open(config) as file:
        data = json.load(file)
        if server.id in data:
            return True
        else:

            try:
                with open(config, "w") as file:
                    data[server.id] = default
                    save = json.dumps(data)
                    file.write(save)
                    return True
            except Exception():
                return False

# Retrieves the value of an option from the config
def retrieve(server: discord.Server, option: str):
    if check(server):
        with open(config) as file:
            data = json.load(file)
            try:
                out = data[server.id][option]
            except KeyError:
                try:
                    data[server.id][option] = default[option]
                except KeyError:
                    return False
                out = data[server.id][option]
            return out

# Edits the value of an option in config
def edit(server: discord.Server, option: str, new):
    if check(server):
        with open(config) as file:
            data = json.load(file)
            data[server.id][option] = new
        with open(config, "w") as edit:
            save = json.dumps(data)
            edit.write(save)
        return True
