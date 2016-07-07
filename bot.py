#Importing things that need importing, woahhh
import discord
from discord.ext import commands
from utils import checks

#Set's bot's desciption and prefixes in a list
description = "An autistic bot for an autistic group of people"
bot = commands.Bot(command_prefix=['!','?','gafbot/','gafbot '], description=description)

###################
## Startup Stuff ##
###################

@bot.event
async def on_ready():
    # Outputs login data to console
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    # Changes the bot's game to default
    await bot.change_status(discord.Game(name="Long Live GAF"))

    # Outputs the state of loading the modules to the console
    # So I know they have loaded correctly
    bot.load_extension("modules.memes")
    print("Loaded Memes")
    bot.load_extension("modules.moderation")
    print("Loaded Moderation")
    bot.load_extension("modules.rng")
    print("loaded RNG")
    bot.load_extension("modules.copypasta")
    print("Loaded Copypastas")
    bot.load_extension("modules.subscriptions")
    print("Loaded Subscriptions")
    bot.load_extension("rss.rss")
    print("Loaded RSS")
    bot.load_extension("modules.csgo")
    print("Loaded CSGO")

####################
##Misc and Testing##
####################

# Command to update the bot's profile picture
# Because Fuyu told me off for doing it everytime
@bot.command(hidden=True)
@checks.is_admin()
async def updateimage():
    #Loads and sets the bot's profile image
    with open("logo.jpg","rb") as logo:
        await bot.edit_profile(avatar=logo.read())

# Greet command
# Also for testing the response of the bot
# Was orignally a trial for me learning how to mention people
# But I couldn't really think of a use so here it is
@bot.command(pass_context=True, hidden=True)
async def greet(ctx):
    """Greets the user"""
    member = ctx.message.author
    server = member.server
    message = "Hello {0.mention}, you're on {1.name}"
    await bot.say(message.format(member, server))
    print("Greeted {0.name}".format(member))

#Ping Pong
#Testing the response of the bot
@bot.command(hidden=True)
async def ping():
    """Pong"""
    await bot.say("Pong")
    print("Ping Pong")

##############
##Announcing##
##############

#Displays a message when a user joins the server
#Needs reworking so it doesn't just work on the GAF server
#I'll do it later
@bot.event
async def on_member_join(member):
    server = member.server
    if server.id == "172425299559055381":
        fmt = '**{0.name}** joined {1.name}'
        channel = discord.Object('173196847060484097')
        role = discord.Object('179618172511584256')
        await bot.add_roles(member, role)
        await bot.send_message(channel, fmt.format(member, server))
        print(fmt.format(member, server))

# Displays a message when a user leaves the server
# Also needs reworking
@bot.event
async def on_member_remove(member):
    server = member.server
    if server.id == "172425299559055381":
        fmt = '**{0.name}** left {1.name}'
        channel = discord.Object('173196847060484097')
        await bot.send_message(channel, fmt.format(member, server))
        print(fmt.format(member, server))

# Displays a message when a user is banned
@bot.event
async def on_member_ban(member):
    server = member.server
    if server.id == "172425299559055381":
        fmt = '**{0.name}** was banned from {1.name}'
        channel = discord.Object('173196847060484097')
        await bot.send_message(channel, fmt.format(member, server))
        print(fmt.format(member, server))

############################
##FANCY TOKEN LOGIN STUFFS##
############################

with open("token.txt","r") as token:
    bot.run(token.read())
