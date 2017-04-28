import discord
from discord.ext import commands
import json
import datetime
import time
from logbook import Logger, StreamHandler
import sys
import inspect
import sqlite3
import asyncio

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
    for x in _df_modules.keys():
        if x not in _modules.keys():
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

async def _get_server_data(server_id):
    c.execute("SELECT * FROM serverSettings WHERE id=?", (server_id,))
    _data = c.fetchone()
    if _data is None:
        c.execute("INSERT INTO serverSettings VALUES (?, ?)", (server_id, default_server_settings))
        conn.commit()
        return default_server_settings
    s_settings = json.loads(_data[1])
    return s_settings

async def _update_server_data(server_id, json_blob):
    save_data = json.dumps(json_blob)
    c.execute("UPDATE serverSettings SET settings='?' WHERE id=?", (save_data, server_id))
    conn.commit()

_prefixes = {}

async def get_prefix(self, ctx):
    if ctx.guild.id in _prefixes:
        return _prefixes[ctx.guild.id]
    else:
        settings = await _get_server_data(ctx.guild.id)
        print(settings)
        _prefixes[ctx.guild.id] = settings["prefix"]
        return _prefixes[ctx.guild.id]

description = """Hi! I'm GAF Bot, a Discord bot written in Python using Discord.py. I was written by DiNitride,
                through many hours of hard work and swearing at my PC.
                I'm kind of like a spork, I'm multifunctional, but still kind of shit. Something you get for novelty
                rather than functionality."""

bot = commands.Bot(command_prefix=get_prefix, description=description)

log.info("Transferring configuration data to bot")
bot.log = log
bot.log.info("Logger linked to bot")
bot.config = _config
bot.log.info("Config linked to bot")
bot.modules = _modules
bot.log.info("Module loading linked to bot")

def command_debug_message(ctx, name):
    if isinstance(ctx.channel, discord.DMChannel):
        bot.log.debug("Command: {} run in DM's by user {}/{}".format(name, ctx.author, ctx.author.id))
    elif isinstance(ctx.channel, discord.GroupChannel):
        bot.log.debug("Command: {} run in group chat {}/{} by user {}/{}".format(name, ctx.channel.name, ctx.channel.id,
                                                                                 ctx.author, ctx.author.id))
    else:
        bot.log.debug("Command: {} run in channel #{}/{} on server {}/{} by user {}/{}".format(name,
                        ctx.channel.name, ctx.channel.id, ctx.guild, ctx.guild.id, ctx.author, ctx.author.id))

bot.cmd_log = command_debug_message

@bot.event
async def on_ready():
    bot.log.notice("Logged in as {} with ID {}".format(bot.user.name, bot.user.id))
    _users = 0
    _channels = 0
    for user in bot.get_all_members():
        _users += 1
    for channel in bot.get_all_channels():
        _channels += 1
    bot.log.notice("I can see {} users in {} channels on {} guilds".format(_users, _channels, len(bot.guilds)))


@bot.command()
async def ping(ctx):
    """Pong"""
    before = time.monotonic()
    await (await bot.ws.ping())
    after = time.monotonic()
    _ping = (after - before) * 1000
    await ctx.send("Ping Pong :ping_pong: **{0:.0f}ms**".format(_ping))
    bot.cmd_log(ctx, "Ping Pong")

bot.run(bot.config["token"])
