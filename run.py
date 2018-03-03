import json

from bot.bot import Bot
from bot.utils.tools import merge_dicts

description = "Hi! I'm GAF Bot, a Discord bot written in Python using Discord.py. " \
              "I was written by DiNitride, through many hours of hard work and swearing at my PC. \n" \
              "I'm kind of like a spork, I'm multifunctional, but still kind of shit. Something you get for novelty " \
              "rather than functionality. You can join my Discord server for more help, reporting bugs, " \
              "or speaking to the developer here by doing $server\n\n"

try:
    with open("bot/config/config.json") as f:
        config = json.load(f)
    with open("bot/config/defaults/default.config.json") as df:
        df_config = json.load(df)
    config = merge_dicts(df_config, config)
    data = json.dumps(config, indent=4, separators=(',', ':'))
    with open("bot/config/config.json", "w") as f:
        f.write(data)
except FileNotFoundError:
    with open("bot/config/defaults/default.config.json") as df:
        config = json.load(df)
        with open("bot/config/config.json", "w") as f:
            f.write(json.dumps(config, indent=4, separators=(',', ':')))

bot = Bot(
    description=description,
    config=config,
)

bot.run()

