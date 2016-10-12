import discord
from discord.ext import commands
from utils import checks
import datetime


def time():
    return datetime.datetime.now().strftime("[%b/%d/%Y %H:%M:%S]")

def log(type: str, message: str):
    print("{:24} {:25} {}".format(time(), type, message))

class Logging():
    def __init__(self, bot):
        self.bot = bot

    async def on_member_join(self, member):
        server = member.server
        if self.bot.settings.retrieve(server, "logging") is True:
            fmt = '**{0.name}** joined {1.name}'
            channel = discord.Object(self.bot.settings.retrieve(server, "log_channel"))
            await self.bot.send_message(channel, fmt.format(member, server))

        msg = "{} joined {}".format(member.name, server.name)
        log("[JOIN]", msg)


        if self.bot.settings.retrieve(server, "role_on_join") is True:
            role = discord.Object(self.bot.settings.retrieve(server, "join_role"))
            await self.bot.add_roles(member, role)

    async def on_member_remove(self, member):
        server = member.server
        if self.bot.settings.retrieve(server, "logging") is True:
            fmt = '**{0.name}** left {1.name}'
            channel = discord.Object(self.bot.settings.retrieve(server, "log_channel"))
            await self.bot.send_message(channel, fmt.format(member, server))

        msg = "{} left {}".format(member.name, server.name)
        log("[LEAVE]", msg)

    async def on_member_ban(self, member):
        server = member.server
        if self.bot.settings.retrieve(server, "logging") is True:
            fmt = '**{0.name}** was banned from {1.name}'
            channel = discord.Object(self.bot.settings.retrieve(server, "log_channel"))
            await self.bot.send_message(channel, fmt.format(member, server))

        msg = "{} was banned from {}".format(member.name, server.name)
        log("[BAN]", msg)

    async def on_member_unban(self, server, member):
        if self.bot.settings.retrieve(server, "logging") is True:
            fmt = '**{0.name}** was unbanned from {1.name}'
            channel = discord.Object(self.bot.settings.retrieve(server, "log_channel"))
            await self.bot.send_message(channel, fmt.format(member, server))

        msg = "{} was unbanned from {}".format(member.name, server.name)
        log("[UNBAN]", msg)

    async def on_message(self, message):
        if str(message.content) == "":
            content = "Image Attachement: {} {}".format(message.attachments[0]["filename"], message.attachments[0]["url"])
        else:
            content = str(message.content)
        msg = "{} | #{} | {} : {}".format(str(message.server.name), str(message.channel.name), str(message.author), str(content))
        log("[MSG RECIEVE]", msg)

    async def on_message_delete(self, message):
        if str(message.content) == "":
            content = "Image Attachement: {} {}".format(message.attachments[0]["filename"], message.attachments[0]["url"])
        else:
            content = str(message.content)
        msg = "{} | #{} | {} : {}".format(str(message.server.name), str(message.channel.name), str(message.author), str(content))
        log("[MSG DELETE]", msg)

    async def on_message_edit(self, message, edit):
        msg = "{} | #{} | {} : {} to {}".format(str(message.server.name), str(message.channel.name), str(message.author), str(message.content), str(edit.content))
        log("[MSG EDIT]", msg)




def setup(bot):
    bot.add_cog(Logging(bot))
