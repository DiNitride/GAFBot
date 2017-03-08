import discord
from discord.ext import commands
import json
from utils import checks
import datetime
import asyncio

class Voice():
    def __init__(self, bot):
        self.bot = bot
        self.instances = {}

    @commands.check(checks.is_owner)
    @commands.group(pass_context=True, invoke_without_command=True)
    async def music(self, ctx):
        await self.bot.say("Music time")

    @commands.check(checks.is_owner)
    @music.command(name="connect", pass_context=True)
    async def music_connect(self, ctx):
        server = ctx.message.server
        channel = ctx.message.author.voice.voice_channel
        if channel is None:
            await self.bot.say("You must be in a voice channel")
            return
        voice = await self.bot.join_voice_channel(channel)
        self.instances[server.id] = {"voice_connection": voice, "queue": [], "current_player": None, "playing": False}

    @commands.check(checks.is_owner)
    @music.command(name="disconnect", pass_context=True)
    async def music_disconnect(self, ctx):
        server = ctx.message.server
        await self.instances[server.id]["voice_connection"].disconnect()
        del self.instances[server.id]

    @commands.check(checks.is_owner)
    @music.command(name="queue", pass_context=True)
    async def music_queue(self, ctx, url: str):
        server = ctx.message.server
        if len(self.instances[server.id]["queue"]) >= 50:
            await self.bot.say("Reached Queue limit")
            return
        voice = self.instances[server.id]["voice_connection"]
        player = await voice.create_ytdl_player(url, ytdl_options={"noplaylist": True, "skipdownload": True})
        self.instances[server.id]["queue"].append({"url": url, "title": player.title, "length": player.duration, "author": player.uploader})
        await self.bot.say("Queued Song: {} by {} [{}]".format(player.title, player.uploader, player.duration))

    @commands.check(checks.is_owner)
    @music.command(name="play", pass_context=True)
    async def music_play(self, ctx):
        server = ctx.message.server
        if self.instances[server.id]["playing"] is False:
            if self.instances[server.id]["voice_connection"] is None:
                await self.bot.say("You must connect the bot before playing music")
                return
            if self.instances[server.id]["current_player"] is not None:
                player = self.instances[server.id]["current_player"]
            elif len(self.instances[server.id]["queue"]) != 0:
                song = self.instances[server.id]["queue"].pop(0)
                player = await self.instances[server.id]["voice_connection"].create_ytdl_player(song["url"], ytdl_options={"noplaylist": True})
                self.instances[server.id]["current_player"] = player
                self.instances[server.id]["current_player"].start()
                await self.bot.say("Now Playing: {} by {} [{}]".format(player.title, player.uploader, player.duration))
            else:
                await self.bot.say("You must queue at least 1 song before playing")
                return

            self.instances[server.id]["playing"] = True
            _time_out = 3
            while True:
                if self.instances[server.id]["current_player"].is_done():
                    if len(self.instances[server.id]["queue"]) != 0:
                        song = self.instances[server.id]["queue"].pop(0)
                        player = await self.instances[server.id]["voice_connection"].create_ytdl_player(song["url"], ytdl_options={"noplaylist": True})
                        self.instances[server.id]["current_player"] = player
                        self.instances[server.id]["current_player"].start()
                        await self.bot.say("Now Playing: {} by {} [{}]".format(player.title, player.uploader, player.duration))
                    elif _time_out == 0:
                        # disconnect
                        await self.instances[server.id]["voice_connection"].disconnect()
                        del self.instances[server.id]
                    else:
                        await asyncio.sleep(60)
                        _time_out -= 1

    @commands.check(checks.is_owner)
    @music.command(name="upnext", pass_context=True)
    async def music_upnext(self, ctx):
        counter = 1
        server = ctx.message.server
        output = "```\nSong Queue:\n"
        for song in self.instances[server.id]["queue"]:
            if len(output) >= 1800:
                output += "```"
                await self.bot.say(output)
                output = "```\n"
            output += "{}. {}\n".format(counter, song["title"])

        output += "```"
        await self.bot.say(output)

def setup(bot):
    bot.add_cog(Voice(bot))
