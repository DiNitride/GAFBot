import discord
from discord.ext import commands
import json
from utils import net
from utils import rates
import base64

class Spotify():
    def __init__(self, bot):
        self.bot = bot
        self.instances = []

    @commands.command(pass_context=True)
    async def spotify(self, ctx, *, search):
        """Searches Spotify for a song
        Usage:
        $spotify song_name
        To filter by artist, use 'by'
        $spotify song_name by artist"""

        author = ctx.message.author

        check = await rates.check(command="spotify", id=author.id, timer=15)
        if check is False:
            return

        if search is None:
            await self.bot.say("Please search something")
            return

        if "by" in search:
            song, artist = search.split("by")
            song = song.strip()
            artist = artist.strip()
            song = song.replace(" ", "+")
            artist = artist.replace(" ", "+")
            api_url = "https://api.spotify.com/v1/search?q=track:{0}+artist:{1}&type=track".format(song, artist)
        else:
            song = search.strip()
            song = song.replace(" ", "+")
            api_url = "https://api.spotify.com/v1/search?q=track:{0}&type=track".format(song)

        response, json, status = await net.get_url(api_url, {"user-agent" : "GAF Bot"})

        if status == 404:
            await self.bot.say("Error: No song found")
            return

        elif status == 504:
            await self.bot.say("Server error")
            return

        song_list = ""
        counter = 0

        for entry in range(len(json["tracks"]["items"])):
            if counter == 5:
                break
            artist_name = ""
            name = json["tracks"]["items"][entry]["name"]
            popularity = json["tracks"]["items"][entry]["popularity"]
            link = json["tracks"]["items"][entry]["external_urls"]["spotify"]
            album = json["tracks"]["items"][entry]["album"]["name"]
            if len(json["tracks"]["items"][entry]["artists"]) > 1:
                for x in range(len(json["tracks"]["items"][entry]["artists"])):
                    artist_name = artist_name + json["tracks"]["items"][entry]["artists"][x]["name"] + ", "
                artist_name = artist_name.rstrip(", ")
            else:
                artist_name = json["tracks"]["items"][entry]["artists"][0]["name"]
            song_list = song_list + ("Name: **{0}**\n"
                                     "Album: **{1}**\n"
                                     "Artist: **{2}**\n"
                                     "Popularity: **{3}**\n"
                                     "Listen: <{4}>\n\n".format(name, album, artist_name, popularity, link))

            counter += 1

        await self.bot.say("Top {0} Songs from search: *{1}*\n\n{2}".format(counter, search, song_list))

    @commands.command(pass_context=True)
    async def playlists(self, ctx):
        """Get's Spotifys daily playlists
        Usage:
        $playlists"""

        author = ctx.message.author
        client_id = self.bot.config["api_keys"]["spotify_client"]
        client_secret = self.bot.config["api_keys"]["spotify_secret"]

        check = await rates.check(command="spotify", id=author.id, timer=15)
        if check is False:
            return

        auth_decoded = "{0}:{1}".format(client_id, client_secret)
        b = bytes(auth_decoded, 'utf-8')
        auth_id = base64.b64encode(b)

        _, auth, status = await net.post_url(
            api_auth_url,
            data={"grant_type" : "client_credentials"}, headers={"Authorization": "Basic {0}".format(auth_id.decode())})

        if status != 200:
            await self.bot.say("Error")
            return

        _, json, status = await net.get_url(
            api_url,
            {"user-agent": "GAF Bot", "Authorization": "Bearer {0}".format(auth["access_token"])})

        if status != 200:
            await self.bot.say("Error")
            return

        playlists = ""
        counter = 0

        for entry in range(len(json["playlists"])):

            if counter == 5:
                break

            name = json["playlists"]["items"][entry]["name"]
            tracks = json["playlists"]["items"][entry]["tracks"]["total"]
            link = json["playlists"]["items"][entry]["external_urls"]["spotify"]



            playlists = playlists + ("Name: **{0}**\n"
                                     "Tracks: **{1}**\n"
                                     "Listen: <{2}>\n\n".format(name, tracks, link))

            counter += 1

        await self.bot.say("__**{0}**__\n\n{1}".format(json["message"], playlists))

def setup(bot):
    bot.add_cog(Spotify(bot))