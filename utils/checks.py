from discord.ext import commands
import discord

# Checks if the message author's id matches the owner
# Owner being me because I'm better than you all
def is_owner_check(message):
    return message.author.id == '95953002774413312'

# Runs the commands module check thing
def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))

# Checks if the message author's roles
def is_admin_check(message, check):
    author = message.author
    role = discord.utils.find(check, author.roles)
    return role is not None

# Checks whether the message author has admin role or is
def is_admin():
    def predicate(ctx):
        if is_owner_check(ctx.message):
            return True
        return is_admin_check(ctx.message, lambda r: r.id == '172426922947641344')
    return commands.check(predicate)