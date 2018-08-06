import dinnerplate
from utils.help_formatter import HelpFormatter
from utils.errors import UserBlacklisted

GAF = dinnerplate.Bot()
GAF.formatter = HelpFormatter()
GAF.add_error_message(UserBlacklisted, "`You are blacklisted`")
GAF.run()
