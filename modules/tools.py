import discord
from discord.ext import commands
import json
from utils import net
from utils import rates

with open("config/config.json") as data:
    config = json.load(data)

class Tools():
    def __init__(self, bot):
        self.bot = bot
        self.instances = []

    @commands.command(pass_context=True)
    async def spotify(self, ctx, *, search):
        """Searches Spotify for a song.
               Search by song name, e.g.
               $spotify songname
               To specify and artist, us 'by', e.g.
               $spotify songname by artist"""

        author = ctx.message.author

        check = await rates.check(command="spotify", id=author.id, timer=15)
        if check is False:
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

        response, json, status = await net.get_url(api_url, "GAF Bot")

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
            song_list = song_list + ("Name: **{0}**\nAlbum: **{1}**\nArtist: **{2}**\nPopularity: **{3}**\nListen: <{4}>\n\n".format(name, album,
                                                                                                     artist_name,
                                                                                                     popularity, link))

            counter += 1

        await self.bot.say("Top 5 Songs from search: *{0}*\n\n{1}".format(search, song_list))


def setup(bot):
    bot.add_cog(Tools(bot))