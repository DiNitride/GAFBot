import json
import datetime
import time
import sys
import inspect
import sqlite3

import discord
from discord.ext import commands
from logbook import Logger, StreamHandler

from utils import checks

StreamHandler(sys.stdout).push_application()
log = Logger("GAF Bot")

log.notice("Loading Configuration File")
try:
    with open("config/config.json") as f:
        _config = json.load(f)
except FileNotFoundError:
    log.error("Config file not found, loading defaults")
    df = open("config/defaults/default.config.json")
    _config = json.load(df)
    with open("config/config.json", "w") as f:
        log.info("Saved new config to file")
        f.write(json.dumps(_config))

try:
    with open("config/modules.json") as f:
        _modules = json.load(f)
    with open("config/defaults/default.modules.json") as df:
        _df_modules = json.load(df)
    for x in list(_df_modules):
        if x not in list(_modules):
            _modules[x] = _df_modules[x]
    data = json.dumps(_modules)
    with open("config/modules.json", "w") as f:
        f.write(data)
except FileNotFoundError:
    log.error("Module loading list not found, loading defaults")
    with open("config/defaults/default.modules.json") as df:
        _modules = json.load(df)
    with open("config/modules.json", "w") as f:
        log.info("Saved module loading to file")
        f.write(json.dumps(_modules))

log.notice("Loading default server settings")
with open("config/defaults/default.serverconfig.json") as f:
    default_server_settings = json.load(f)

log.notice("Establishing connection to database")
conn = sqlite3.connect('config/serverSettings.db')
log.notice("Established connection")
c = conn.cursor()
c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='serverSettings'")
exists = c.fetchone()
if not exists[0]:
    c.execute('''CREATE TABLE serverSettings (id bigint, settings long)''')
    log.notice("Settings table did not exist, created new table")

async def get_server_data(server_id):
    c.execute("SELECT * FROM serverSettings WHERE id=?", (server_id,))
    _data = c.fetchone()
    if _data is None:
        c.execute("INSERT INTO serverSettings VALUES (?, ?)", (server_id, json.dumps(default_server_settings)))
        conn.commit()
        return default_server_settings
    s_settings = json.loads(_data[1])
    for x in default_server_settings.keys():
        if x not in s_settings.keys():
            s_settings[x] = default_server_settings[x]
    for m in _modules.keys():
        if m not in s_settings["modules"]:
            s_settings["modules"][m] = _modules[m]
    save_data = json.dumps(s_settings)
    c.execute("UPDATE serverSettings SET settings=? WHERE id=?", (save_data, server_id))
    conn.commit()
    return s_settings

async def update_server_data(server_id, json_blob):
    save_data = json.dumps(json_blob)
    c.execute("UPDATE serverSettings SET settings=? WHERE id=?", (save_data, server_id))
    conn.commit()

_prefixes = {}

async def get_prefix(_bot, ctx):
    r = [_bot.user.mention + " ", "<@!{}s> ".format(_bot.user.id)]
    if ctx.guild.id in _prefixes:
        r.append(_prefixes[ctx.guild.id])
        return r
    else:
        settings = await get_server_data(ctx.guild.id)
        _prefixes[ctx.guild.id] = settings["prefix"]
        r.append(_prefixes[ctx.guild.id])
        return r

async def update_prefix_cache(guild_id: int, prefix: str):
    _prefixes[guild_id] = prefix

async def get_prefix_via_id(guild_id):
    if guild_id in _prefixes:
        return _prefixes[guild_id]
    else:
        settings = await get_server_data(guild_id)
        _prefixes[guild_id] = settings["prefix"]
        return _prefixes[guild_id]

description = """Hi! I'm GAF Bot, a Discord bot written in Python using Discord.py. I was written by DiNitride,
                through many hours of hard work and swearing at my PC.
                I'm kind of like a spork, I'm multifunctional, but still kind of shit. Something you get for novelty
                rather than functionality."""

bot = commands.Bot(command_prefix=get_prefix, description=description, pm_help=True)

log.info("Transferring configuration data to bot")
bot.log = log
bot.log.info("Logger linked to bot")
bot.config = _config
bot.log.info("Config linked to bot")
bot.modules = _modules
bot.log.info("Module loading linked to bot")

bot.get_server_data = get_server_data
bot.update_server_data = update_server_data
bot.update_prefix_cache = update_prefix_cache

bot.command_count = 0

async def check_command(ctx):
    server = await bot.get_server_data(ctx.guild.id)
    module = ctx.command.cog_name
    if module is None:
        return True
    module = module.lower()
    return server["modules"][module]

bot.add_check(check_command)


@bot.event
async def on_ready():
    bot.start_time = datetime.datetime.now()
    bot.log.notice("Logged in as {} with ID {}".format(bot.user.name, bot.user.id))
    users = sum(1 for user in bot.get_all_members())
    channels = sum(1 for channel in bot.get_all_channels())
    bot.log.notice("I can see {} users in {} channels on {} guilds".format(users, channels, len(bot.guilds)))

    # Load Modules
    bot.load_extension("modules.config")
    bot.log.notice("Loaded Config Module")
    bot.load_extension("modules.statistics")
    bot.log.notice("Loaded Statistics Module")
    bot.load_extension("modules.roles")
    bot.log.notice("Loaded Roles Module")
    bot.load_extension("modules.admin")
    bot.log.notice("Loaded Admin Module")
    bot.load_extension("modules.moderation")
    bot.log.notice("Loaded Moderation Module")
    bot.load_extension("modules.gaf")
    bot.log.notice("Loaded GAF Module")


@bot.event
async def on_command(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        bot.log.debug("Command: '{}' run in DM's by user {} - ({})".format(
            ctx.command, ctx.author, ctx.author.id))
    elif isinstance(ctx.channel, discord.GroupChannel):
        bot.log.debug("Command: '{}' run in group chat {} - ({}) by user {} - {{}}".format(
            ctx.command, ctx.channel.name, ctx.channel.id, ctx.author, ctx.author.id))
    else:
        bot.log.debug("Command: '{}' run in channel #{} - ({}) on server {} - ({}) by user {} - ({})".format(
            ctx.command, ctx.channel.name, ctx.channel.id, ctx.guild, ctx.guild.id, ctx.author, ctx.author.id))
    bot.command_count += 1


@bot.command()
async def about(ctx):
    """Information about GAF Bot"""
    if ctx.channel.permissions_for(ctx.guild.me).embed_links:
        embed = discord.Embed(title="Invite me to your server!", colour=discord.Colour.gold(),
                              url="https://discordapp.com/oauth2/authorize?&client_id=173708503796416512&scope=bot&permissions=8",
                              description="Hi! I'm GAF Bot, a Discord bot written in Python using Discord.py."
                                          "I was written by DiNitride, through many hours of hard work and swearing "
                                          "at my PC. I'm kind of like a spork, I'm multifunctional, but still kind of "
                                          "shit. Something you get for novelty rather than functionality.",
                              timestamp=datetime.datetime.utcfromtimestamp(1493993514))

        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_author(name="GAF Bot", url="https://github.com/DiNitride/GAFBot")

        embed.add_field(name="Source Code", value="https://github.com/DiNitride/GAFBot")
        embed.add_field(name="Author", value="GAF Bot is written and maintained by DiNitride#7899")
        embed.add_field(name="Discord.py Version", value=discord.__version__)
        embed.add_field(name="The Never Ending GAF", value="GAF Bot is the bot of the awful community known as "
                                                           "The Never Ending GAF, which you can find out about at "
                                                           "http://www.neverendinggaf.com")

        await ctx.send(embed=embed)
    else:
        await ctx.send("**Hi!** I'm GAF Bot, a Discord bot written in Python using Discord.py."
                       "I was written by DiNitride, through many hours of hard work and swearing at my PC. "
                       "*I'm kind of like a spork, I'm multifunctional, but still kind of shit.*"
                       "Something you get for novelty rather than functionality.\n"
                        "GAF Bot is the bot of the awful community known as **The Never Ending GAF**, "
                       "which you can find out about at <http://www.neverendinggaf.com>\n"
                       "**Invite link:** <https://discordapp.com/oauth2/authorize?&client_id=173708503796416512&scope=bot&permissions=8>\n"
                       "**Author:** DiNitride#7899\n"
                       "**Source Code:** <https://github.com/DiNitride/GAFBot>"
                       )


@bot.command()
@checks.is_owner()
async def ping(ctx):
    """Pong"""
    before = time.monotonic()
    await (await bot.ws.ping())
    after = time.monotonic()
    _ping = (after - before) * 1000
    await ctx.send("Ping Pong :ping_pong: **{0:.0f}ms**".format(_ping))


@bot.command(name="eval")
@checks.is_owner()
async def _eval(ctx, *, code):
    """Evaluates a line of code provided"""
    heck = "off"
    hel = "yea"
    fuck = "off"
    code = code.strip("` ")
    try:
        result = eval(code)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        await ctx.send("```py\nInput: {}\n{}: {}```".format(code, type(e).__name__, e))
    else:
        await ctx.send("```py\nInput: {}\nOutput: {}\n```".format(code, result))
    await ctx.message.delete()


@bot.command()
async def f(ctx):
    """Pays resepect"""
    await ctx.send("*Respects*")


async def save_module_loading():
    _data = json.dumps(bot.modules)
    with open("config/modules.json", "w") as f:
        f.write(_data)
        bot.log.notice("Saved module list")


@bot.command(name="load")
@checks.is_owner()
async def _load(ctx, extension: str):
    """Enables a module"""
    extension = extension.lower()
    if extension not in bot.modules.keys():
        bot.log.error("Tried to enable module {} but it is not a valid module".format(extension))
        await ctx.send("Invalid module")
        bot.cmd_log(ctx, "Attempted to enable invalid module")
    else:
        bot.modules[extension] = True
        bot.log.debug("Unloading extension")
        bot.unload_extension("modules." + extension)
        bot.log.debug("Loading extension")
        bot.load_extension("modules." + extension)
        bot.log.notice("Enabled Module")
        await ctx.send("Enabled Module")
        await save_module_loading()


@bot.command(name="unload")
@checks.is_owner()
async def _unload(ctx, extension: str):
    """Disables a module"""
    extension = extension.lower()
    if extension not in bot.modules.keys():
        bot.log.error("Tried to disable module {} but it is not a valid module".format(extension))
        await ctx.send("Invalid module")
    else:
        bot.modules[extension] = False
        bot.log.debug("Unloading extension")
        bot.unload_extension("modules." + extension)
        bot.log.debug("Loading extension")
        bot.load_extension("modules." + extension)
        bot.log.notice("Disabled module {}".format(extension))
        await ctx.send("Disabled Module")
        await save_module_loading()

try:
    bot.run(bot.config["token"])
except discord.errors.LoginFailure:
    bot.log.critical("Improper token passed, quitting process")
