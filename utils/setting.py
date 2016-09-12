from discord.ext import commands
import discord
import json

default = {"logging" : False, "log_channel" : "", "role_on_join" : False, "join_role" : ""}

def is_in_data(server):
    if isinstance(server, __import__("discord").Message):
        server = server.server
    with open("config/serversettings.json") as file:
        data = json.load(file)
        if server.id in data:
            return True # continue with command
        else:
            try:
                with open("config/serversettings.json","w") as file:
                    data[server.id] = default
                    save = json.dumps(data)
                    file.write(save)
                    return True
            except Exception():
                return False