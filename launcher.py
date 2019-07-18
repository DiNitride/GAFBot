import dinnerplate

from discord.ext.commands import MinimalHelpCommand
from utils.errors import UserBlacklisted
from utils.help_formatter import Help

GAF = dinnerplate.Bot()
GAF.add_error_message(UserBlacklisted, "`You are blacklisted`")
GAF.help_command = Help()
GAF.run()
