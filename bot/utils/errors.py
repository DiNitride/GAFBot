import discord
from discord.ext import commands


class NoEmbedsError(commands.CommandError):
    """
    An exception when the bot does not have embed permissions and a command is ran.
    """
    pass

class CogDisabledError(commands.CommandError):
    """
    An exception raised when a cog is disabled.
    """
    pass
