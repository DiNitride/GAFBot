import asyncio
import time
import json

with open("config/config.json") as file:
    config = json.load(file)

blacklist = {
    "spotify" : {},
    "ping" : {},
    "csgo" : {},
    "overwatch" : {},
    "general" : {}
}

async def check(command, id, timer):

    if id == config["ids"]["owner"]:
        return True

    check = id in blacklist[command].keys()

    if check is False:
        blacklist[command][id] = time.time() + timer
        return True

    if blacklist[command][id] <= time.time():
        blacklist[command][id] = time.time() + timer
        return True
    else:
        return False
