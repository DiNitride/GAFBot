import json
import datetime
import time
import sys
import inspect
import sqlite3
import subprocess
import traceback

import discord
from discord.ext import commands
from discord.ext.commands import CommandError, CheckFailure, UserInputError, \
    DisabledCommand, CommandOnCooldown, NotOwner, NoPrivateMessage, CommandInvokeError, \
    CommandNotFound
from logbook import Logger, StreamHandler

from utils import checks
from utils.errors import NoEmbedsError, CogDisabledError
from utils.helpFormatter import MyHelpFormatter

# TODO: Logging to file
# TODO: Backing up config
StreamHandler(sys.stdout).push_application()
log = Logger("GAF Bot")

log.notice("Loading Configuration File")
try:
    with open("config/config.json") as f:
        _config = json.load(f)
    with open("config/defaults/default.config.json") as df:
        _df_config = json.load(df)
    for x in list(_df_config):
        if x not in list(_config):
            _config[x] = _df_config[x]
    data = json.dumps(_config)
    with open("config/config.json", "w") as f:
        f.write(data)
except FileNotFoundError:
    log.error("Config file not found, loading defaults")
    df = open("config/defaults/default.config.json")
    _config = json.load(df)
    with open("config/config.json", "w") as f:
        log.info("Saved new config to file")
        f.write(json.dumps(_config, indent=4, separators=(',', ':')))

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
    try:
        if ctx.guild.id in _prefixes:
            r.append(_prefixes[ctx.guild.id])
            return r
        else:
            settings = await get_server_data(ctx.guild.id)
            _prefixes[ctx.guild.id] = settings["prefix"]
            r.append(_prefixes[ctx.guild.id])
            return r
    except AttributeError:
        return r.append("$")

async def update_prefix_cache(guild_id: int, prefix: str):
    _prefixes[guild_id] = prefix

async def get_prefix_via_id(guild_id):
    if guild_id in _prefixes:
        return _prefixes[guild_id]
    else:
        settings = await get_server_data(guild_id)
        _prefixes[guild_id] = settings["prefix"]
        return _prefixes[guild_id]

description = "Hi! I'm GAF Bot, a Discord bot written in Python using Discord.py. " \
              "I was written by DiNitride, through many hours of hard work and swearing at my PC. \n" \
              "I'm kind of like a spork, I'm multifunctional, but still kind of shit. Something you get for novelty " \
              "rather than functionality. You can join my Discord server for more help, reporting bugs, " \
              "or speaking to the developer here by doing $server\n\n" \


help_ext = "Many of the commands are subcommands, so do $help <command> for more detail on them\n"

bot = commands.Bot(command_prefix=get_prefix, description=description + help_ext, pm_help=True, formatter=MyHelpFormatter())

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

bot.default_guild_config = default_server_settings

bot.command_count = 0

async def update_config(key, value):
    """
    Updates a value in the bots config.
    """
    bot.config[key] = value
    with open("config/config.json", 'w') as f:
        f.write(json.dumps(bot.config, indent=4, separators=(',', ':')))

bot.update_config = update_config


async def check_command(ctx):
    server = await bot.get_server_data(ctx.guild.id)
    module = ctx.command.cog_name
    if module is None:
        return True
    module = module.lower()
    if server["modules"][module]:
        return server["modules"][module]
    else:
        raise CogDisabledError

bot.add_check(check_command)


@bot.event
async def on_ready():
    bot.start_time = datetime.datetime.now()
    bot.log.notice("Logged in as {} with ID {}".format(bot.user.name, bot.user.id))
    users = sum(1 for user in bot.get_all_members())
    channels = sum(1 for channel in bot.get_all_channels())
    bot.log.notice("I can see {} users in {} channels on {} guilds".format(users, channels, len(bot.guilds)))
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
    bot.load_extension("modules.utils")
    bot.log.notice("Loaded Utils Module")
    bot.load_extension("modules.spotify")
    bot.log.notice("Loaded Spotify")
    bot.load_extension("modules.rng")
    bot.log.notice("Loaded RNG")
    bot.load_extension("modules.csgo")
    bot.log.notice("Loaded CS:GO")
    bot.load_extension("modules.pubg")
    bot.log.notice("Loaded PUBG")


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


@bot.event
async def on_command_error(context, exception: CommandError):
    # stolen from Union bc I cba to write the same thing
    # thnx laura
    # https://github.com/DBDU/union/blob/master/union/core/bot.py#L102

    args = ' '.join(exception.args)

    if isinstance(exception, CheckFailure) and not isinstance(exception, NoPrivateMessage):
        message = f"\N{NO ENTRY SIGN} Checks failed: {args}"
    elif isinstance(exception, NoPrivateMessage):
        message = f"\N{CROSS MARK} This command does not work in private messages."
    elif isinstance(exception, UserInputError):
        message = f"\N{CROSS MARK} {args}"
    elif isinstance(exception, DisabledCommand):
        message = f"\N{CROSS MARK} The command {context.invoked_with} is disabled."
    elif isinstance(exception, CommandOnCooldown):
        message = f"\N{CROSS MARK} The command {context.invoked_with} is on cooldown. " \
                f"Try again in {exception.retry_after:.2f} seconds."
    elif isinstance(exception, NotOwner):
        message = f"\N{NO ENTRY SIGN} You are not the bot owner."
    elif isinstance(exception, NoEmbedsError):
        message = f"\N{CROSS MARK} Command {context.invoked_with} requires the bot to have embed permissions"
    elif isinstance(exception, CommandNotFound):
        message = f"\N{LEFT-POINTING MAGNIFYING GLASS} Command {context.invoked_with} does not exist"
    elif isinstance(exception, CogDisabledError):
        message = f"\N{CROSS MARK} `{context.invoked_with}` is from a bot module that is disabled"
    # Danger Zone
    elif isinstance(exception, CommandInvokeError):
        message = f"\N{SQUARED SOS} An internal error has occurred."
        print(traceback.print_exception(type(exception.__cause__), exception.__cause__,
                                  exception.__cause__.__traceback__))
    else:
        message = f"\N{BLACK QUESTION MARK ORNAMENT} An unknown error has occurred."
        traceback.print_exception(type(exception), exception, exception.__traceback__)

    await context.send(message)


@bot.command()
@checks.has_embeds()
async def info(ctx):
    """Information about GAF Bot"""
    with ctx.channel.typing():
        embed = discord.Embed(title="Invite me to your server!", colour=discord.Colour.gold(),
                                url="https://discordapp.com/oauth2/authorize?&client_id=173708503796416512&scope=bot&permissions=8",
                              description=description,
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


@bot.command()
async def source(ctx):
    """
    Source code
    """
    await ctx.send("https://github.com/DiNitride/GAFBot")


@bot.command()
async def server(ctx):
    """
    Invite to the bot's guild[2].text)
    """
    await ctx.send("<http://discord.bot.neverendinggaf.com> - https://discord.gg/ddbFt7S")


@bot.command()
async def invite(ctx):
    """
    Invite link to add the bot to your guild
    """
    await ctx.send("`Invite me to your server! <https://discordapp.com/oauth2/authorize?&client_id=173708503796416512&scope=bot&permissions=8>")


@bot.command()
@checks.is_owner()
async def ping(ctx):
    """
    Pong
    """
    before = time.monotonic()
    await (await bot.ws.ping())
    after = time.monotonic()
    _ping = (after - before) * 1000
    await ctx.send("Ping Pong :ping_pong: **{0:.0f}ms**".format(_ping))


@bot.command(hidden=True)
@checks.is_owner()
async def update(ctx):
    """
    Updates the bot
    """
    await ctx.send("Calling process to update! :up: :date: ")
    try:
        done = subprocess.run("git pull", shell=True, stdout=subprocess.PIPE, timeout=30)
        if done:
            message = done.stdout.decode()
            await ctx.send("`{}`".format(message))
            if message == "Already up-to-date.\n":
                await ctx.send("No update available :no_entry:")
            else:
                await ctx.send("Succesfully updated! Rebooting now :repeat: ")
                await bot.logout()
    except subprocess.CalledProcessError:
        await ctx.send("Error updating! :exclamation: ")
    except subprocess.TimeoutExpired:
        await ctx.send("Error updating - Process timed out! :exclamation: ")


@bot.command(name="eval")
@checks.is_owner()
async def _eval(ctx, *, code):
    """
    Evaluates a line of code provided
    """
    hel = "yea"
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
    """
    Pays resepect
    """
    await ctx.send("*Respects*")


async def save_module_loading():
    _data = json.dumps(bot.modules)
    with open("config/modules.json", "w") as f:
        f.write(_data)
        bot.log.notice("Saved module list")


@bot.command(name="load")
@checks.is_owner()
async def _load(ctx, extension: str):
    """
    Enables a module
    """
    extension = extension.lower()
    if extension not in bot.modules.keys():
        bot.log.error   ("Tried to enable module {} but it is not a valid module".format(extension))
        await ctx.send("Invalid module")
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
    """
    Disables a module
    """
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
