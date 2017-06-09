import base64
import datetime
import random

import discord
from discord.ext import commands

from utils import net


class Spotify:

    def __init__(self, bot):
        self.bot = bot
        self.auth_id = self.bot.config["spotify"]["id"]
        self.auth_secret = self.bot.config["spotify"]["secret"]

    @commands.command()
    async def search(self, ctx, *, search: str):
        """Searches Spotify"""
        song = search.strip()
        song = song.replace(" ", "+")
        api_url = "https://api.spotify.com/v1/search?q=track:{0}&type=track".format(song)
        api_auth_url = 'https://accounts.spotify.com/api/token'

        auth_decoded = "{0}:{1}".format(self.auth_id, self.auth_secret)
        b = bytes(auth_decoded, 'utf-8')
        auth_id = base64.b64encode(b)

        _, auth, status = await net.post_url(
            api_auth_url,
            data={"grant_type": "client_credentials"}, headers={"user-agent": "GAF Bot", "Authorization": "Basic {0}".format(auth_id.decode())})

        response, json, status = await net.get_url(api_url, {"user-agent": "GAF Bot", "Authorization": "Bearer {}".format(auth["access_token"])})

        embed = discord.Embed(title="Showing top 5 results", colour=discord.Colour.green(),
                              timestamp=datetime.datetime.utcfromtimestamp(1493993514))

        embed.set_author(name="Spotify search results for: {}".format(search))
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/2000px-Spotify_logo_without_text.svg.png")
        embed.set_footer(text="Spotify and related assets copyright respective owners")

        counter = 0
        if ctx.channel.permissions_for(ctx.guild.me).embed_links:
            with ctx.channel.typing():
                for entry in json["tracks"]["items"]:
                    if counter == 5:
                        break
                    content = "Appears on album: {}\nPopularity Rating: {}\n[Listen here]({})".format(entry["album"]["name"], entry["popularity"], entry["external_urls"]["spotify"])
                    if len(entry["artists"]) > 1:
                        artist_names = ""
                        for x in range(len(entry["artists"])):
                            artist_names += entry["artists"][x]["name"] + ", "
                        artist_names = artist_names[:-2]
                        content = "Other Artists: {}\n".format(artist_names) + content
                    embed.add_field(
                        name="{} by {}".format(entry["name"], entry["artists"][0]["name"]),
                        value=content,
                        inline=False)
                    counter += 1

                await ctx.send(embed=embed)
        else:
            await ctx.send("Honestly I can't be bothered to format this for non-embeds yet and really, who doesn't have embeds on now, c'mon just give the bot embed permissions you're missing out")

    @commands.command()
    async def playlists(self, ctx):
        """Get's todays daily playlists"""
        api_url = "https://api.spotify.com/v1/browse/featured-playlists?limit=5"
        api_auth_url = 'https://accounts.spotify.com/api/token'

        auth_decoded = "{0}:{1}".format(self.auth_id, self.auth_secret)
        b = bytes(auth_decoded, 'utf-8')
        auth_id = base64.b64encode(b)

        _, auth, status = await net.post_url(
            api_auth_url,
            data={"grant_type": "client_credentials"},
            headers={"user-agent": "GAF Bot", "Authorization": "Basic {0}".format(auth_id.decode())})

        response, json, status = await net.get_url(api_url, {"user-agent": "GAF Bot",
                                                             "Authorization": "Bearer {}".format(auth["access_token"])})
        if ctx.channel.permissions_for(ctx.guild.me).embed_links:
            with ctx.channel.typing():
                embed = discord.Embed(title="Today's Daily Playlists", colour=discord.Colour.green(),
                                      timestamp=datetime.datetime.utcfromtimestamp(1493993514))

                embed.set_author(name="{}".format(json["message"]))
                embed.set_thumbnail(
                    url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/2000px-Spotify_logo_without_text.svg.png")
                embed.set_footer(text="Spotify and related assets copyright respective owners")

                for entry in json["playlists"]["items"]:
                    embed.add_field(
                        name="{}".format(entry["name"]),
                        value="Total Tracks: {}\n[Listen here]({})".format(entry["tracks"]["total"], entry["external_urls"]["spotify"]),
                        inline=False)

                await ctx.send(embed=embed)
        else:
            await ctx.send("Honestly I can't be bothered to format this for non-embeds yet and really, who doesn't have embeds on now, c'mon just give the bot embed permissions you're missing out")

    @commands.command()
    async def playlist(self, ctx):
        """Picks a random playlist from 20 of the daily playlists"""
        api_url = "https://api.spotify.com/v1/browse/featured-playlists"
        api_auth_url = 'https://accounts.spotify.com/api/token'

        auth_decoded = "{0}:{1}".format(self.auth_id, self.auth_secret)
        b = bytes(auth_decoded, 'utf-8')
        auth_id = base64.b64encode(b)

        _, auth, status = await net.post_url(
            api_auth_url,
            data={"grant_type": "client_credentials"},
            headers={"user-agent": "GAF Bot", "Authorization": "Basic {0}".format(auth_id.decode())})

        response, json, status = await net.get_url(api_url, {"user-agent": "GAF Bot",
                                                             "Authorization": "Bearer {}".format(auth["access_token"])})

        playlist = json["playlists"]["items"][random.randint(0,19)]

        if ctx.channel.permissions_for(ctx.guild.me).embed_links:
            with ctx.channel.typing():
                embed = discord.Embed(title="Listen Here", colour=discord.Colour.green(),
                                      url= playlist["external_urls"]["spotify"],
                                      timestamp=datetime.datetime.utcfromtimestamp(1493993514))

                embed.set_author(name="{}".format(playlist["name"]), icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Spotify_logo_without_text.svg/2000px-Spotify_logo_without_text.svg.png")
                embed.set_thumbnail(
                    url=playlist["images"][0]["url"])
                embed.set_footer(text="Spotify and related assets copyright respective owners")
                embed.add_field(name="Track count", value="{}".format(playlist["tracks"]["total"]))

                await ctx.send(embed=embed)
        else:
            message = "Daily Playlist: **{}** *({} Songs)* - __Listen here: <{}>__".format(playlist["name"], playlist["tracks"]["total"], playlist["external_urls"]["spotify"])
            await ctx.send(message)


def setup(bot):
    bot.add_cog(Spotify(bot))