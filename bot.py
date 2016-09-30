import discord
from discord.ext import commands
import json
from utils import setting
from utils import checks
from utils import rates

# Set's bot's desciption and prefixes in a list
description = "An autistic bot for an autistic group"
bot = commands.Bot(command_prefix=['$'], description=description, pm_help=True)

###################
## Startup Stuff ##
###################

@bot.event
async def on_ready():

    # Load config file
    with open("config/config.json") as data:
        bot.config = json.load(data)

    # Outputs login data to console
    print("-----------------------------------------")
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print("-----------------------------------------")
    await bot.change_presence(game=discord.Game(name="Long Live GAF"))
    print("Set Status to Long Live GAF")
    print("-----------------------------------------")

    # Outputs the state of loading the modules to the console
    # So I know they have loaded correctly
    print("Loading Modules")
    print("-----------------------------------------")
    bot.load_extension("modules.misc")
    print("Loaded Misc")
    bot.load_extension("modules.moderation")
    print("Loaded Moderation")
    bot.load_extension("modules.rng")
    print("loaded RNG")
    bot.load_extension("modules.subscriptions")
    print("Loaded Subscriptions")
    bot.load_extension("rss.rss")
    print("Loaded RSS")
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
    with open("config/ignored.json") as file:
        ignored = json.load(file)
    file.close()
    if message.author.id in ignored:
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
    """Ignores a user from using the bot"""
    if user is None:
        return
    if user.id is "95953002774413312":
        return
    with open("config/ignored.json") as file:
        ignored = json.load(file)
        if user.id not in ignored:
            ignored.append(user.id)
            with open("config/ignored.json", "w") as file:
                save = json.dumps(ignored)
                file.write(save)
            await bot.say("User {0} ignored :no_entry_sign:".format(user.name))
        else:
            ignored.remove(user.id)
            with open("config/ignored.json", "w") as file:
                save = json.dumps(ignored)
                file.write(save)
            await bot.say("User {0} unignored :white_check_mark:".format(user.name))


# Greet command
# Also for testing the response of the bot
# Was originally a trial for me learning how to mention people
# But I couldn't really think of a use so here it is
@bot.command(pass_context=True, hidden=True)
async def greet(ctx):
    """Greets the user"""
    member = ctx.message.author
    server = member.server
    message = "Hello {0.mention}, you're on {1.name}"
    await bot.say(message.format(member, server))
    print("Greeted {0.name}".format(member))

# Ping Pong
# Testing the response of the bot
@bot.command(pass_context=True)
async def ping():
    """Pong"""
    await bot.say("Pong")
    print("Ping Pong")

# Invite link to the bot server
@bot.command()
async def server():
    """The bot's server, for updates or something"""
    await bot.say("https://discord.gg/Eau7uhf")
    print("Run: Server")

# Bot's source code
@bot.command()
async def source():
    """Source code"""
    await bot.say("https://github.com/DiNitride/GAFBot")
    print("Run: Source")

@bot.command()
async def botinfo():
    """Info on the bot"""
    await bot.say("""```xl\nOwner: DiNitride\nGithub: https://github.com/DiNitride/GAFBot\nServer: https://discord.gg/Eau7uhf\n```""")

#############
## Logging ##
#############

# Displays a message when a user joins the server
@bot.event
async def on_member_join(member):
    server = member.server
    if setting.retrieve(server, "logging") is True:
        fmt = '**{0.name}** joined {1.name}'
        channel = discord.Object(setting.retrieve(server, "log_channel"))
        await bot.send_message(channel, fmt.format(member, server))
        print(fmt.format(member, server))
    if setting.retrieve(server, "role_on_join") is True:
        role = discord.Object(setting.retrieve(server, "join_role"))
        await bot.add_roles(member, role)

# Displays a message when a user leaves the server
@bot.event
async def on_member_remove(member):
    server = member.server
    if setting.retrieve(server, "logging") is True:
        fmt = '**{0.name}** left {1.name}'
        channel = discord.Object(setting.retrieve(server, "log_channel"))
        await bot.send_message(channel, fmt.format(member, server))
        print(fmt.format(member, server))


# Displays a message when a user is banned
@bot.event
async def on_member_ban(member):
    server = member.server
    if setting.retrieve(server, "logging") is True:
        fmt = '**{0.name}** was banned from {1.name}'
        channel = discord.Object(setting.retrieve(server, "log_channel"))
        await bot.send_message(channel, fmt.format(member, server))
        print(fmt.format(member, server))

# Displays a message when a user is unbanned
@bot.event
async def on_member_unban(server, member):
    if setting.retrieve(server, "logging") is True:
        fmt = '**{0.name}** was unbanned from {1.name}'
        channel = discord.Object(setting.retrieve(server, "log_channel"))
        await bot.send_message(channel, fmt.format(member, server))
        print(fmt.format(member, server))


#################################
## Changing Command Categories ##
#################################

bot.get_command("help").cog_name = "..Core.."
bot.get_command("server").cog_name = "..Core.."
bot.get_command("botinfo").cog_name = "..Core.."
bot.get_command("source").cog_name = "..Core.."
bot.get_command("ping").cog_name = "Fuck Fuzen"

##############################
## FANCY TOKEN LOGIN STUFFS ##
##############################

with open("config/token.txt") as token:
    bot.run(token.read())

