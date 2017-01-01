import discord
from discord.ext import commands
import json
from utils import setting
from utils import checks
from utils import rates
from utils import logging
import asyncio
import inspect

"""
GAF Bot - https://github.com/DiNitride/GAFBot
Written with love by DiNitride
https://github.com/DiNitride
"""

# Set's bot's desciption and prefixes in a list
description = """
Hi! I'm GAF Bot, a Discord bot written in Python using Discord.py. I was written by DiNitride,
through many hours of hard work and swearing at my PC.
I'm kind of like a spork, I'm multifunctional, but still kind of shit. Something you get for novelty
rather than functionality.

Owner: DiNitride
Github: https://github.com/DiNitride/GAFBot
Invite Link: https://discordapp.com/oauth2/authorize?&client_id=173708503796416512&scope=bot&permissions=8
"""

bot = commands.Bot(command_prefix=['$'], description=description, pm_help=True)

log = logging.Logging

# Load config file
with open("config/config.json") as data:
    bot.config = json.load(data)

    bot.settings = setting.Settings()

# Load ignored users
with open("config/ignored.json") as file:
    bot.ignored = json.load(file)

# Load tags
with open("config/tags.json") as file:
    bot.tags = json.load(file)

###################
## Startup Stuff ##
###################

@bot.event
async def on_ready():

    # Outputs login data to console
    print("-----------------------------------------")
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print("-----------------------------------------")
    if bot.user.id == "195466701360332803":
        await bot.change_presence(game=discord.Game(name="Development"))
        print("Set Status to Development")
    else:
        await bot.change_presence(game=discord.Game(name="Long Live GAF"))
        print("Set Status to Long Live GAF")
    print("-----------------------------------------")

    # Outputs the state of loading the modules to the console
    # So I know they have loaded correctly
    print("Loading Modules")
    print("-----------------------------------------")
    bot.load_extension("utils.logging")
    print("Loaded Logging")
    bot.load_extension("modules.misc")
    print("Loaded Misc")
    bot.load_extension("modules.moderation")
    print("Loaded Moderation")
    bot.load_extension("modules.rng")
    print("loaded RNG")
    bot.load_extension("modules.subscriptions")
    print("Loaded Subscriptions")
    # bot.load_extension("rss.rss")
    # print("Loaded RSS")
    bot.load_extension("modules.csgo")
    print("Loaded CS:GO")
    bot.load_extension("modules.config")
    print("Loaded Config")
    bot.load_extension("modules.tags")
    print("Loaded Tags")
    bot.load_extension("modules.gaf")
    print("Loaded GAF")
    bot.load_extension("modules.overwatch")
    print("Loaded Overwatch")
    bot.load_extension("modules.spotify")
    print("Loaded Spotify")
    bot.load_extension("modules.admin")
    print("Loaded Admin")
    print("-----------------------------------------")

    await save_configs()

# Setting category of commands in core file
# Because "no category" bothered me
# I don't know how this works tbh
# Emoticon told me what to do
def get_category(self):
    if self.instance is not None:
        return type(self.instance).__name__
    else:
        try:
            return self._category
        except AttributeError:
            return None

def set_category(self, category):
    self._category = category

commands.Command.cog_name = property(get_category, set_category)

@bot.event
async def on_message(message):

    # Check if user is ignored
    if message.author.id in bot.ignored:
        return

    # General Ratelimiting
    check = await rates.check(command="general", id=message.author.id, timer=bot.config["settings"]["ratelimit"])
    if check is False:
        return

    await bot.process_commands(message)

######################
## Misc and Testing ##
######################

# Command to update the bot's profile picture
# Because Fuyu told me off for doing it every time
@bot.command(hidden=True)
@commands.check(checks.is_owner)
async def updateprofile():
    """Updates the bot's profile image"""
    # Loads and sets the bot's profile image
    with open("logo.jpg","rb") as logo:
        await bot.edit_profile(avatar=logo.read())

@bot.command(hidden=True)
@commands.check(checks.is_owner)
async def ignore(user: discord.Member = None):
    """Ignores or uningores a user from using the bot
    Usage:
    $ignore @recchan"""
    if user is None:
        return
    if user.id is "95953002774413312":
        return
    if user.id not in bot.ignored:
        bot.ignored.append(user.id)
        await bot.say("User {0} ignored :no_entry_sign:".format(user.name))
    else:
        bot.ignored.remove(user.id)
        await bot.say("User {0} unignored :white_check_mark:".format(user.name))

# Greet command
# Also for testing the response of the bot
# Was originally a trial for me learning how to mention people
# But I couldn't really think of a use so here it is
@bot.command(pass_context=True, hidden=True)
async def greet(ctx):
    """Greets the user
    Usage:
    $greet"""
    member = ctx.message.author
    server = member.server
    message = "Hello {0.mention}, you're on {1.name}"
    await bot.say(message.format(member, server))

# Ping Pong
# Testing the response of the bot
@bot.command(pass_context=True)
async def ping():
    """Pong
    Usage:
    Ask Fuzen"""
    await bot.say("Pong")

# Invite link to the bot server
@bot.command()
async def server():
    """The bot's server, for updates or something
    Usage:
    $server"""
    await bot.say("https://discord.gg/Eau7uhf")

# Bot's source code
@bot.command()
async def source():
    """Source code
    Usage:
    $source"""
    await bot.say("https://github.com/DiNitride/GAFBot")

@bot.command()
async def about():
    """Info on the bot
    Usage:
    $about"""
    list = []
    for x in bot.servers:
        list.append(x.name)

    await bot.say("Hi! I'm GAF Bot, a Discord bot written in Python using Discord.py. I was written by "
                  "DiNitride, through many hours of hard work and swearing at my PC.\n"
                  "I'm kind of like a spork, I'm multifunctional, but still kind of shit. "
                  "Something you get for novelty rather than functionality.\n\n"
                  "**Owner:** DiNitride\n"
                  "**Github:** <https://github.com/DiNitride/GAFBot>\n"
                  "**Server:** https://discord.gg/Eau7uhf\n"
                  "**Servers:** {}\n"
                  "**Invite Link:** "
                  "<https://discordapp.com/oauth2/authorize?&client_id=173708503796416512&scope=bot&permissions=8>"
                  .format(len(list)))

@bot.command(pass_context=True, name="eval", hidden=True)
@commands.check(checks.is_owner)
async def eval_(ctx, *, code: str):
    """Evaluates a line of code provided"""
    code = code.strip("` ")
    server = ctx.message.server
    message = ctx.message
    try:
        result = eval(code)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        await bot.say("```py\nInput: {}\n{}: {}```".format(code, type(e).__name__, e))
    else:
        await bot.say("```py\nInput: {}\nOutput: {}\n```".format(code, result))
    await bot.delete_message(message)

async def save_configs():
    while True:

        # Save Tags
        with open("config/tags.json", "w") as file:
            save = json.dumps(bot.tags)
            file.write(save)

        # Save ignored users
        with open("config/ignored.json", "w") as file:
            save = json.dumps(bot.ignored)
            file.write(save)

        logging.log("[SYSTEM]", "Saved tags and ignore list")
        await asyncio.sleep(60)


#################################
## Changing Command Categories ##
#################################

bot.get_command("help").cog_name = "..Core.."
bot.get_command("server").cog_name = "..Core.."
bot.get_command("about").cog_name = "..Core.."
bot.get_command("source").cog_name = "..Core.."
bot.get_command("ping").cog_name = "Fuck Fuzen"

##############################
## FANCY TOKEN LOGIN STUFFS ##
##############################

print("Logging into dev account")
try:
    with open("dev_token.txt") as token:
        bot.run(token.read())
except FileNotFoundError:
    print("Logging into main account")
    token = bot.config["api_keys"]["discord"]
    bot.run(token)

print("Logging out of bot")
