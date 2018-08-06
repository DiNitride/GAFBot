from discord.ext import commands


def is_gaf_server():
    def predicate(ctx):
        return ctx.message.guild.id == 172425299559055381
    return commands.check(predicate)
