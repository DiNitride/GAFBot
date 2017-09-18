import json
import sys
import datetime
import traceback
import sqlite3

import discord
from discord.ext import commands
from discord.ext.commands import CommandError, CheckFailure, UserInputError, \
    DisabledCommand, CommandOnCooldown, NotOwner, NoPrivateMessage, CommandInvokeError, \
    CommandNotFound
from logbook import Logger, StreamHandler, FileHandler

from bot.utils.help_formatter import HelpFormatter
from bot.utils.errors import NoEmbedsError, CogDisabledError
from bot.utils.tools import merge_dicts


class Bot(commands.AutoShardedBot):

    def __init__(self,
                 description,
                 config,
                 ):

        self.config = config
        self.config = config
        self.logger = None
        self.db_conn = None
        self.db_cursor = None
        self.command_count = 0
        self.default_guild_config = None
        self._prefix_cache = {}
        self.startup = None

        super().__init__(
            command_prefix='~~',
            description=description,
            pm_help=True,
            formatter=HelpFormatter()
        )

    async def prefix(self, bot, ctx):
        r = [f"{bot.user.mention} ", f"<@!{bot.user.id} "]
        try:
            if ctx.guild.id in self._prefix_cache:
                return r.append(self._prefix_cache[ctx.guild.id])
            else:
                self._prefix_cache[ctx.guild.id] = await self.get_guild_settings(ctx.guild.id)["prefix"]
                return r.append(self._prefix_cache[ctx.ctx.guild.id])
        except AttributeError:
            return r.append("$")

    async def get_guild_config(self, guild_id: int):
        self.db_cursor.execute("SELECT * FROM guild_config WHERE id=?", (guild_id,))
        config = self.db_cursor.fetchone()
        if config is None:
            self.db_cursor.execute("INSERT INTO serverSettings VALUES (?, ?)",
                                   (guild_id, json.dumps(self.default_guild_config)))
            self.db_conn.commit()
            return self.default_guild_config
        config = merge_dicts(self.default_guild_config, config[1])
        self.db_cursor.execute("UPDATE serverSettings SET settings=? WHERE id=?", (json.dumps(config), guild_id))
        self.db_conn.commit()
        return config

    async def set_guild_config(self, guild_id: int, config):
        self.db_cursor.execute("UPDATE serverSettings SET settings=? WHERE id=?", (json.dumps(config), guild_id))
        self.db_conn.commit()

    async def update_config(self, new_config):
        self.config = new_config
        with open("config/config.json", 'w') as f:
            f.write(json.dumps(self.config, indent=4, separators=(',', ':')))

    def on_ready(self):
        self.startup = datetime.datetime.now()
        self.logger.notice(f"Logged in as {self.user.name} with ID {self.user.id}")
        users = sum(1 for user in self.get_all_members())
        channels = sum(1 for channel in self.get_all_channels())
        self.logger.notice("I can see {} users in {} channels on {} guilds".format(users, channels, len(self.guilds)))
        super().add_check(self.cog_enabled_check)

    async def on_command(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            self.logger.debug(f"Command: '{ctx.command}' "
                              f"User: '{ctx.author}'/{ctx.author.id} (In DM's)")
        else:
            self.logger.debug(f"Command: {ctx.command} "
                              "Channel '#{cxt.channel.name}'/{ctx.channel.id} "
                              "Guild '{ctx.guild}'/{ctx.guild.id} "
                              "User: '{ctx.author}'/{ctx.author.id}")
        self.command_count += 1

    async def on_command_error(self, context, exception: CommandError):

        if isinstance(exception, CommandNotFound):
            return

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
        elif isinstance(exception, CogDisabledError):
            message = f"\N{CROSS MARK} `{context.invoked_with}` is from a bot module that is disabled"
        elif isinstance(exception, CommandInvokeError):
            message = f"\N{SQUARED SOS} An internal error has occurred."
            print(traceback.print_exception(type(exception.__cause__), exception.__cause__,
                                            exception.__cause__.__traceback__))
        else:
            message = f"\N{BLACK QUESTION MARK ORNAMENT} An unknown error has occurred."
            traceback.print_exception(type(exception), exception, exception.__traceback__)

        await context.send(message)

    async def cog_enabled_check(self, ctx):
        guild_config = await self.get_guild_config(ctx.guild.id)
        cog = ctx.command.cog_name
        if cog is None:
            return True
        if guild_config["modules"][cog.lower()]:
            return guild_config["modules"][cog.lower()]
        else:
            raise CogDisabledError

    def run(self):

        log = Logger("GAF Bot")
        log.handlers.append(StreamHandler(sys.stdout, bubble=True))
        log.handlers.append(FileHandler("bot/logs/last-run.log", bubble=True, mode="w"))
        self.logger = log

        with open("bot/config/defaults/default.guildconfig.json") as f:
            self.default_guild_config = json.load(f)

        self.db_conn = sqlite3.connect("bot/config/serverSettings.db")
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='serverSettings'")
        exists = self.db_cursor.fetchone()
        if not exists[0]:
            self.db_cursor.execute('''CREATE TABLE serverSettings (id bigint, settings long)''')

        super().run(self.config["token"], reconnect=True)


