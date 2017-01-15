import asyncio
import time
import json

with open("config/config.json") as file:
    config = json.load(file)
file.close()

# update this so the blacklist type is passed in with the check function
# rather than each one having to be hardcoded in later
# because you're lazy and don't want to do that
# (which is why you're not doing it now and are writing this comment)
# (why are you like this james)

blacklist = {
    "spotify": {},
    "ping": {},
    "csgo": {},
    "overwatch": {},
    "general": {}
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
