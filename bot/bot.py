import json
import sys
import datetime
import traceback
import sqlite3
import time

import discord
from discord.ext import commands
from discord.ext.commands import CommandError, CheckFailure, UserInputError, \
    DisabledCommand, CommandOnCooldown, NotOwner, NoPrivateMessage, CommandInvokeError, \
    CommandNotFound
from logbook import Logger, StreamHandler, FileHandler
import tqdm

from bot.utils.help_formatter import HelpFormatter
from bot.utils.errors import NoEmbedsError, BotCogDisabledError, GuildCogDisabledError
from bot.utils.tools import merge_dicts
from bot.utils.net import post_url


class Bot(commands.AutoShardedBot):

    def __init__(self,
                 description,
                 config,
                 ):

        self.config = config

        super().__init__(
            command_prefix=self.prefix,
            description=description,
            pm_help=True,
            formatter=HelpFormatter()
        )

        self.logger = None
        self.db_conn = None
        self.db_cursor = None
        self.command_count = 0
        self.default_guild_config = None
        self.prefix_cache = {}
        self.startup = None
        self.add_check(self.cog_enabled_check)
        self.log_channels = {
            "guild": None
        }

    async def prefix(self, bot, ctx):
        r = [f"{bot.user.mention} ", f"<@!{bot.user.id}> "]
        try:
            if ctx.guild.id in self.prefix_cache:
                r.append(self.prefix_cache[ctx.guild.id])
                return r
            else:
                guild_config = await self.get_guild_config(ctx.guild.id)
                self.prefix_cache[ctx.guild.id] = guild_config["prefix"]
                r.append(self.prefix_cache[ctx.guild.id])
                return r
        except AttributeError:
            r.append("$")
            return r

    async def get_guild_config(self, guild_id: int):
        # self.logger.debug(f"Getting guild {guild_id} config")
        self.db_cursor.execute("SELECT * FROM serverSettings WHERE id=?", (guild_id,))
        config = self.db_cursor.fetchone()
        if config is None:
            self.logger.debug(f"Guild {guild_id} config did not exist! Creating an entry with default values")
            self.db_cursor.execute("INSERT INTO serverSettings VALUES (?, ?)",
                                   (guild_id, json.dumps(self.default_guild_config)))
            self.db_conn.commit()
            return self.default_guild_config
        config = json.loads(config[1])
        config = merge_dicts(self.default_guild_config, config)
        self.db_cursor.execute("UPDATE serverSettings SET settings=? WHERE id=?", (json.dumps(config), guild_id))
        self.db_conn.commit()
        return config

    async def set_guild_config(self, guild_id: int, config):
        self.db_cursor.execute("UPDATE serverSettings SET settings=? WHERE id=?", (json.dumps(config), guild_id))
        self.db_conn.commit()
        self.logger.debug(f"Updated guild {guild_id} config")

    async def update_config(self):
        with open("bot/config/config.json", 'w') as f:
            f.write(json.dumps(self.config, indent=4, separators=(',', ':')))
        self.logger.debug("Updated bot config file")

    async def on_ready(self):
        self.startup = datetime.datetime.now()
        self.logger.notice(f"Logged in as {self.user.name} with ID {self.user.id}")
        self.log_channels["guild"] = self.get_channel(self.config["log_channels"]["guild"])
        self.logger.info(f"Set Guild Log channel to #{self.log_channels['guild']}")
        users = sum(1 for user in self.get_all_members())
        channels = sum(1 for channel in self.get_all_channels())
        self.logger.notice("I can see {} users in {} channels on {} guilds".format(users, channels, len(self.guilds)))

    async def on_command(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            self.logger.debug(f"Command: '{ctx.command}' "
                              f"User: '{ctx.author}'/{ctx.author.id} (In DM's)")
        else:
            self.logger.debug(f"Command: {ctx.command} "
                              f"Channel: '#{ctx.channel.name}'/{ctx.channel.id} "
                              f"Guild: '{ctx.guild}'/{ctx.guild.id} "
                              f"User: '{ctx.author}'/{ctx.author.id}")
        self.command_count += 1

    async def on_command_error(self, context, exception: CommandError):
        # TODO: Make this not shit
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
        elif isinstance(exception, BotCogDisabledError):
            message = f"\N{CROSS MARK} `{context.invoked_with}` is currently disabled on the bot"
        elif isinstance(exception, GuildCogDisabledError):
            message = f"\N{CROSS MARK} `{context.invoked_with}` is disabled for this guild"
        elif isinstance(exception, CommandInvokeError):
            message = f"\N{SQUARED SOS} `An internal error has occurred.`"
            print(traceback.print_exception(type(exception.__cause__), exception.__cause__,
                                            exception.__cause__.__traceback__))
        else:
            message = f"\N{BLACK QUESTION MARK ORNAMENT} An unknown error has occurred."
            traceback.print_exception(type(exception), exception, exception.__traceback__)

        await context.send(message)

    async def cog_enabled_check(self, ctx):
        cog = ctx.command.cog_name
        guild_config = await self.get_guild_config(ctx.guild.id)

        if cog is None:
            return True

        if cog.lower() == "core":
            return True

        if self.config["modules"][cog.lower()]:
            if guild_config["modules"][cog.lower()]:
                return guild_config["modules"][cog.lower()]
            else:
                raise GuildCogDisabledError
        else:
            raise BotCogDisabledError

    async def on_message(self, message):
        guild_config = await self.get_guild_config(message.guild.id)
        if guild_config["inviteCop"] is True and message.channel.id not in guild_config["inviteCopPassChannels"]:
            if "discord.gg" in message.content or "discordapp.com/invite/" in message.content:
                await message.delete()
                channels = await self.get_formatted_list_of_invite_cop_bypass_channels(message.guild.id)
                await message.channel.send(f"Invites are not allowed in this channel\n"
                                           f"```\n{channels}\n```")
                return
        if message.author.bot is True:
            return
        if message.author.id in self.config["user_blacklist"]:
            return
        if message.content == "dab" and message.guild.id == 172425299559055381:
            await message.channel.send("<o/")
        await self.process_commands(message)

    async def get_formatted_list_of_invite_cop_bypass_channels(self, guild_id):
        guild_config = await self.get_guild_config(guild_id)
        resp = "Invite Permitted Channels:\n"
        if len(guild_config["inviteCopPassChannels"]) != 0:
            for c in guild_config["inviteCopPassChannels"]:
                channel = self.get_channel(c)
                resp += f"#{channel}\n"
        else:
            resp += "None"
        return resp

    def sum_users_and_channels(self):
        """
        Calculates total sum of users and channels that the bot can "see"
        """
        users = sum(1 for user in self.get_all_members())
        channels = sum(1 for channel in self.get_all_channels())
        return users, channels

    def calculate_uptime(self):
        """
        Calculates uptime of bot
        """
        current_time = datetime.datetime.now()
        uptime = current_time - self.startup
        days = int(uptime.days)
        hours = int(uptime.seconds / 3600)
        minutes = int((uptime.seconds % 3600) / 60)
        seconds = int((uptime.seconds % 3600) % 60)
        return uptime, days, hours, minutes, seconds

    async def log_to_channel(self, channel: str, message):
        if self.log_channels[channel] is not None:
            await self.log_channels[channel].send(message)

    async def on_guild_join(self, guild):
        msg = f"Joined \"{guild.name}\" owned by {guild.owner}"
        self.logger.info(msg)
        await self.log_to_channel("guild", msg)
        if self.config["guild_announcement_url"]:
            await post_url(self.config["guild_announcement_url"], {"value1": "Joined", "value2": guild.name, "value3": guild.owner})

    async def on_guild_remove(self, guild):
        msg = f"Left \"{guild.name}\" owned by {guild.owner}"
        await self.log_to_channel("guild", msg)
        if self.config["guild_announcement_url"]:
            await post_url(self.config["guild_announcement_url"], {"value1": "Left", "value2": guild.name, "value3": guild.owner})

    def run(self):

        log = Logger("GAF Bot")
        log.handlers.append(StreamHandler(sys.stdout, bubble=True))
        log.handlers.append(FileHandler("bot/logs/last-run.log", bubble=True, mode="w"))
        self.logger = log
        self.logger.notice("Logging started")
        self.logger.notice("Bot process started")

        with open("bot/config/defaults/default.guildconfig.json") as f:
            self.default_guild_config = json.load(f)
            self.logger.debug("Loaded default guild config")

        self.logger.debug("Connecting to DB")
        self.db_conn = sqlite3.connect("bot/config/guild_configs.db")
        self.logger.notice("DB Connection Established")
        self.db_cursor = self.db_conn.cursor()
        self.db_cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='serverSettings'")
        exists = self.db_cursor.fetchone()
        if not exists[0]:
            self.logger.error("No table found in DB! Creating new one now")
            self.db_cursor.execute('''CREATE TABLE serverSettings (id bigint, settings long)''')
            self.logger.debug("Table created")

        self.load_extension("bot.modules.core")
        self.logger.notice("Loaded core module")

        self.logger.notice("Loading other modules")
        # This bar and the time.sleep() stuff is entirely useless
        # Like completely
        # Don't do this
        # It just looks cool and that makes me happy but really this is terrible
        # and a complete waste of time
        time.sleep(0.5)
        for cog in tqdm.tqdm(self.config["modules"].keys(),
                             desc="Loading modules"
                             ):
            self.load_extension(f"bot.modules.{cog.lower()}")
            time.sleep(0.2)
        time.sleep(0.5)
        self.logger.debug("Completed loading modules")

        self.logger.notice("Logging into Discord")
        super().run(self.config["token"], reconnect=True)


