import discord
from discord.ext import commands

from utils import errors


def is_owner_check(ctx):
    return ctx.message.author.id == 95953002774413312


def is_owner():
    return commands.check(is_owner_check)


def is_admin():
    def predicate(ctx):
        if is_owner_check(ctx):
            return True
        message = ctx.message
        channel = message.channel
        perms = channel.permissions_for(message.author)
        perms = channel.permissions_for(message.author)
        return perms.administrator
    return commands.check(predicate)


def perms_manage_roles():
    def predicate(ctx):
        if is_owner_check(ctx):
            return True
        message = ctx.message
        channel = message.channel
        perms = channel.permissions_for(message.author)
        return perms.manage_roles
    return commands.check(predicate)


def perms_manage_guild():
    def predicate(ctx):
        if is_owner_check(ctx):
            return True
        message = ctx.message
        channel = message.channel
        perms = channel.permissions_for(message.author)
        return perms.manage_guild
    return commands.check(predicate)


def perms_manage_messages():
    def predicate(ctx):
        if is_owner_check(ctx):
            return True
        message = ctx.message
        channel = message.channel
        perms = channel.permissions_for(message.author)
        return perms.manage_messages
    return commands.check(predicate)


def perms_manage_channels():
    def predicate(ctx):
        if is_owner_check(ctx):
            return True
        message = ctx.message
        channel = message.channel
        perms = channel.permissions_for(message.author)
        return perms.manage_channels
    return commands.check(predicate)


def perms_ban():
    def predicate(ctx):
        if is_owner_check(ctx):
            return True
        message = ctx.message
        channel = message.channel
        perms = channel.permissions_for(message.author)
        return perms.ban_members
    return commands.check(predicate)


def perms_kick():
    def predicate(ctx):
        if is_owner_check(ctx):
            return True
        message = ctx.message
        channel = message.channel
        perms = channel.permissions_for(message.author)
        return perms.kick_members
    return commands.check(predicate)


def is_gaf_server():
    def predicate(ctx):
        return ctx.message.guild.id == 172425299559055381
    return commands.check(predicate)


def has_embeds():
    def predicate(ctx):
        if ctx.channel.permissions_for(ctx.guild.me).embed_links:
            return True
        else:
            raise errors.NoEmbedsError
            return False
    return commands.check(predicate)
