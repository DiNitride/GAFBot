import datetime

import discord
from discord.ext import commands

from bot.utils import checks


class Utils:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.has_embeds()
    async def whois(self, ctx, id: int):
        """
        Searches for a user via ID
        """
        try:
            with ctx.channel.typing():
                user = await self.bot.get_user_info(id)
                embed = discord.Embed(colour=discord.Colour(0x30f9c7), description="ID: {}".format(user.id),
                                      timestamp=datetime.datetime.now())
                embed.set_thumbnail(
                    url=user.avatar_url)
                embed.set_author(name=user)
                embed.set_footer(text="Who Is")
                embed.add_field(name="Bot?", value=user.bot, inline=False)
                embed.add_field(name="Account Creation Date", value=user.created_at, inline=False)
                await ctx.send(embed=embed)
        except discord.NotFound:
            await ctx.send("`No user found under this ID`")
        except discord.HTTPException:
            await ctx.send("`Error collecting user information`")
            return

    @commands.group(invoke_without_command=True)
    @checks.has_embeds()
    async def about(self, ctx, user: discord.Member = None):
        """
        Shows information about a user, or server
        """
        if user is None:
            user = ctx.author
        with ctx.channel.typing():
            embed = discord.Embed(colour=discord.Colour(0x30f9c7), description="ID: {}".format(user.id),
                                  timestamp=datetime.datetime.now())
            embed.set_thumbnail(
                url=user.avatar_url)
            embed.set_author(name=user)
            embed.set_footer(text="All about {}".format(user))
            embed.add_field(name="Bot?", value=user.bot)
            embed.add_field(name="Roles", value="{}".format(len(user.roles) - 1))
            embed.add_field(name="Account Creation Date", value=user.created_at)
            embed.add_field(name="Date Joined Guild", value=user.joined_at)
            embed.add_field(name="Game", value=user.game)
            embed.add_field(name="Status", value=user.status)
            embed.add_field(name="Voice State", value=user.voice)
            embed.add_field(name="Display Name", value=user.display_name)
            await ctx.send(embed=embed)

    @about.command()
    @checks.has_embeds()
    async def server(self, ctx):
        """
        Basic info on the server
        """
        with ctx.channel.typing():
            embed = discord.Embed(title="ID: 58934178071780", colour=discord.Colour.gold(),
                                  timestamp=datetime.datetime.now())
            embed.set_thumbnail(
                url=ctx.guild.icon_url)
            embed.set_author(name=ctx.guild.name)
            embed.set_footer(text="Who Is")
            embed.add_field(name="Members", value=str(len(ctx.guild.members)))
            embed.add_field(name="Roles", value=str(len(ctx.guild.roles) - 1))
            embed.add_field(name="Channels", value=str(len(ctx.guild.channels)))
            embed.add_field(name="AFK Channel", value=ctx.guild.afk_channel)
            embed.add_field(name="AFK Timeout", value=str(ctx.guild.afk_timeout / 60))
            embed.add_field(name="Owner", value=ctx.guild.owner)
            embed.add_field(name="Creation Date", value=ctx.guild.created_at)
            embed.add_field(name="Region", value=ctx.guild.region)
            embed.add_field(name="Verification Level", value=ctx.guild.verification_level)

            embed.set_footer(text="About Server")
            await ctx.send(embed=embed)

    @commands.command()
    @checks.has_embeds()
    async def avatar(self, ctx, user: discord.Member = None):
        """
        Returns the avatar of a user
        """
        with ctx.channel.typing():
            if user is None:
                user = ctx.author
            embed = discord.Embed(
                url="https://cdn.discordapp.com/avatars/95953002774413312/43731ce5807eb8503cd3559a3c13e780.webp?size=1024",
                timestamp=datetime.datetime.now())
            embed.set_image(
                url="{}".format(user.avatar_url))
            embed.set_author(name="Click for {}'s Avatar".format(user),
                             url=user.avatar_url)

            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utils(bot))
