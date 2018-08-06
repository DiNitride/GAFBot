import base64
import datetime
import random

import discord
from discord.ext import commands
from dinnerplate import BaseCog, JsonConfigManager, has_embeds

from utils import net


SPOTIFY_ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/" \
                   "Spotify_logo_without_text.svg/2000px-Spotify_logo_without_text.svg.png"
AUTH_ENDPOINT = "https://accounts.spotify.com/api/token"
PLAYLIST_ENDPOINT = "https://api.spotify.com/v1/browse/featured-playlists"
DEFAULT = {
    "id": "",
    "secret": ""
}


async def get_auth_token(auth_id):
    return await net.post_url(
        AUTH_ENDPOINT,
        data={
            "grant_type": "client_credentials"
        },
        headers={
            "user-agent": "GAF Bot",
            "Authorization": f"Basic {auth_id.decode()}"
        })


async def get_spotify_endpoint(endpoint, auth_token):
    return await net.get_url(
        endpoint, {
            "user-agent": "GAF Bot",
            "Authorization": f"Bearer {auth_token}"
        })


class Spotify(BaseCog):

    def __init__(self, bot):
        super().__init__(bot)
        self.config = JsonConfigManager("spotify.json", default=DEFAULT)
        self.auth_id = self.config["id"]
        self.auth_secret = self.config["secret"]

    def get_auth_id(self):
        return base64.b64encode(bytes(f"{self.auth_id}:{self.auth_secret}", 'utf-8'))

    @commands.group(hidden=True)
    async def spotify(self, ctx):
        pass

    @spotify.command()
    @has_embeds()
    async def search(self, ctx, *, search: str):
        """
        Searches Spotify
        """
        with ctx.channel.typing():
            search_endpoint = f"https://api.spotify.com/v1/search?q=track:{search.strip().replace(' ', '+')}&type=track"
            auth_id = self.get_auth_id()
            _, auth, status = await get_auth_token(auth_id)
            _, json, status = await get_spotify_endpoint(search_endpoint, auth["access_token"])

            embed = discord.Embed(title="Showing top 5 results",
                                  colour=discord.Colour.green(),
                                  timestamp=datetime.datetime.now())

            embed.set_author(name="Spotify search results for: {}".format(search))
            embed.set_thumbnail(url=SPOTIFY_ICON_URL)
            embed.set_footer(text="Spotify and related assets copyright respective owners")

            counter = 0
            for entry in json["tracks"]["items"]:
                if counter == 5:
                    break
                content = f"Appears on album: {entry['album']['name']}\n" \
                          f"Popularity Rating: {entry['popularity']}\n" \
                          f"[Listen here]({entry['external_urls']['spotify']})"

                if len(entry["artists"]) > 1:
                    artist_names = ""
                    for x in range(len(entry["artists"])):
                        artist_names += entry["artists"][x]["name"] + ", "
                    artist_names = artist_names[:-2]
                    content = f"Other Artists: {artist_names}\n" + content

                embed.add_field(
                    name=f"{entry['name']} by {entry['artists'][0]['name']}",
                    value=content,
                    inline=False)
                counter += 1

            await ctx.send(embed=embed)

    @spotify.command()
    @has_embeds()
    async def playlists(self, ctx):
        """
        Get's todays daily playlists
        """
        with ctx.channel.typing():
            auth_id = self.get_auth_id()
            _, auth, status = await get_auth_token(auth_id)
            _, json, status = await get_spotify_endpoint(PLAYLIST_ENDPOINT + "?limit=5", auth["access_token"])

            embed = discord.Embed(title="Today's Daily Playlists", colour=discord.Colour.green(),
                                  timestamp=datetime.datetime.now())

            embed.set_author(name="{}".format(json["message"]))
            embed.set_thumbnail(
                url=SPOTIFY_ICON_URL)
            embed.set_footer(text="Spotify and related assets copyright respective owners")

            for entry in json["playlists"]["items"]:
                embed.add_field(
                    name="{}".format(entry["name"]),
                    value="Total Tracks: {}\n[Listen here]({})".format(entry["tracks"]["total"],
                                                                       entry["external_urls"]["spotify"]),
                    inline=False)

            await ctx.send(embed=embed)

    @spotify.command()
    @has_embeds()
    async def playlist(self, ctx):
        """
        Picks a random playlist from 20 of the daily playlists
        """
        with ctx.channel.typing():
            auth_id = self.get_auth_id()
            _, auth, status = await get_auth_token(auth_id)
            _, json, status = await get_spotify_endpoint(PLAYLIST_ENDPOINT, auth["access_token"])

            playlist = json["playlists"]["items"][random.randint(0, len(json["playlists"]["items"]))]
            embed = discord.Embed(title="Listen Here", colour=discord.Colour.green(),
                                  url=playlist["external_urls"]["spotify"],
                                  timestamp=datetime.datetime.now())

            embed.set_author(
                name=f"{playlist['name']}",
                icon_url=SPOTIFY_ICON_URL)
            embed.set_thumbnail(
                url=playlist["images"][0]["url"])
            embed.set_footer(text="Spotify and related assets copyright respective owners")
            embed.add_field(name="Track count", value=f"{playlist['tracks']['total']}")

            await ctx.send(embed=embed)


setup = Spotify.setup
