import discord
from discord.ext import commands


class UserBlacklisted(commands.CommandError):
    """
    An exception when the user is blacklisted from the bot
    """
    pass
