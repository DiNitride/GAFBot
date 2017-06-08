import datetime

import discord
from discord.ext import commands

async def construct_serverinfo(obj):
    embed = discord.Embed(title="ID: 58934178071780", colour=discord.Colour(0x610073),
                          timestamp=datetime.datetime.utcfromtimestamp(1491012420))
    embed.set_thumbnail(
        url=obj.icon_url)
    embed.set_author(name=obj.name)
    embed.set_footer(text="Who Is")
    embed.add_field(name="Members", value=str(len(obj.members)))
    embed.add_field(name="Roles", value=str(len(obj.roles) - 1))
    embed.add_field(name="Channels", value=str(len(obj.channels)))
    embed.add_field(name="AFK Channel", value=obj.afk_channel)
    embed.add_field(name="AFK Timeout", value=str(obj.afk_timeout / 60))
    embed.add_field(name="Owner", value=obj.owner)
    embed.add_field(name="Creation Date", value=obj.created_at)
    embed.add_field(name="Region", value=obj.region)
    embed.add_field(name="Verification Level", value=obj.verification_level)

    content = "```\n" \
              "Server Name: {}\nID: {}\n" \
              "Members: {}\n" \
              "Channels: {}\n" \
              "Roles: {}\n" \
              "AFK Channel: {}\n" \
              "AFK Timeout: {}\n" \
              "Owner: {}\n" \
              "Creation Date: {}\n" \
              "Region: {}\n" \
              "Verification Level: {}\n" \
              "```".format(obj.name, obj.id, len(obj.members), len(obj.channels) - 1,
                           len(obj.roles), obj.afk_channel, str(obj.afk_timeout / 60), obj.owner,
                           obj.created_at, obj.region, obj.verification_level)

    return embed, content


class Utils:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def whois(self, ctx, id: int):
        """Searches for a user via ID"""
        try:
            user = await self.bot.get_user_info(id)
            if ctx.channel.permissions_for(ctx.author).embed_links:
                with ctx.channel.typing():
                    embed = discord.Embed(colour=discord.Colour(0x30f9c7), description="ID: {}".format(user.id),
                                          timestamp=datetime.datetime.utcfromtimestamp(1490992111))
                    embed.set_thumbnail(
                        url=user.avatar_url)
                    embed.set_author(name=user)
                    embed.set_footer(text="Who Is")
                    embed.add_field(name="Bot?", value=user.bot, inline=False)
                    embed.add_field(name="Account Creation Date", value="", inline=False)
                    await ctx.send(embed=embed)
            else:
                output = ":mag_right: User Found!\n" \
                         "```\n" \
                         "Name: {}\n" \
                         "ID: {}\n" \
                         "Bot?: {}\n" \
                         "Account Creation Date: {}\n" \
                         "```" \
                         "Avatar: <{}>".format(
                    user, user.id, user.bot, user.created_at, user.avatar_url
                )
                await ctx.send(output)
        except discord.NotFound:
            await ctx.send("`No user found under this ID`")
        except discord.HTTPException:
            await ctx.send("`Error collecting user information`")
            return

    @commands.group(invoke_without_command=True)
    async def about(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if ctx.channel.permissions_for(ctx.author).embed_links:
            with ctx.channel.typing():
                embed = discord.Embed(colour=discord.Colour(0x30f9c7), description="ID: {}".format(user.id),
                                      timestamp=datetime.datetime.utcfromtimestamp(1490992111))
                embed.set_thumbnail(
                    url=user.avatar_url)
                embed.set_author(name=user)
                embed.set_footer(text="All about {}".format(user))
                embed.add_field(name="Bot?", value=user.bot, inline=False)
                embed.add_field(name="Account Creation Date", value=user.created_at, inline=False)
                embed.add_field(name="Date Joined Guild", value=user.joined_at, inline=False)
                embed.add_field(name="Roles", value="{}".format(len(user.roles) - 1), inline=False)
                embed.add_field(name="Game", value=user.game, inline=False)
                embed.add_field(name="Status", value=user.status, inline=False)
                embed.add_field(name="Voice State", value=user.voice, inline=False)
                embed.add_field(name="Display Name", value=user.display_name, inline=False)
                await ctx.send(embed=embed)
        else:
            output = ":mag_right: Info about user\n" \
                     "```\n" \
                     "Name: {}\n" \
                     "ID: {}\n" \
                     "Bot?: {}\n" \
                     "Account Creation Date: {}\n" \
                     "Date Joined Guild: {}\n" \
                     "Roles: {}\n" \
                     "Game: {}\n" \
                     "Status: {}\n" \
                     "Voice State: {}\n" \
                     "Display Name: {}\n" \
                     "```" \
                     "Avatar: <{}>".format(
                user, user.id, user.bot, user.created_at, user.joined_at,len(user.roles) - 1, user.game, user.status,
                user.voice, user.display_name, user.avatar_url
            )
            await ctx.send(output)

    @about.command()
    async def server(self, ctx):
        """Basic info on the server"""
        embed, content = await construct_serverinfo(ctx.guild)
        if ctx.channel.permissions_for(ctx.author).embed_links:
            with ctx.channel.typing():
                embed.set_footer(text="About Server")
                await ctx.send(embed=embed)
        else:
            await ctx.send(content=content)


def setup(bot):
    bot.add_cog(Utils(bot))
