import discord
from discord.ext import commands

class Copypasta():
    def __init__(self, bot):
        self.bot = bot

    #Navy Seal copypasta
    @commands.command()
    async def navyseal(self):
        """Navy Seal Copypasta."""
        await self.bot.say(
            "What the fuck did you just fucking say about me, you little bitch? I’ll have you know I graduated top of my class in the Navy Seals,"
            " and I’ve been involved in numerous secret raids on Al-Quaeda, and I have over 300 confirmed kills. I am trained in gorilla warfare"
            " and I’m the top sniper in the entire US armed forces. You are nothing to me but just another target. I will wipe you the fuck out with"
            " precision the likes of which has never been seen before on this Earth, mark my fucking words. You think you can get away with saying"
            " that shit to me over the Internet? Think again, fucker. As we speak I am contacting my secret network of spies across the USA "
            " your IP is being traced right now so you better prepare for the storm, maggot. The storm that wipes out the pathetic little thing"
            " you call your life. You’re fucking dead, kid. I can be anywhere, anytime, and I can kill you in over seven hundred ways, and that’s"
            " just with my bare hands. Not only am I extensively trained in unarmed combat, but I have access to the entire arsenal of the United"
            " States Marine Corps and I will use it to its full extent to wipe your miserable ass off the face of the continent, you little shit."
            " If only you could have known what unholy retribution your little “clever” comment was about to bring down upon you, maybe you would"
            " have held your fucking tongue. But you couldn’t, you didn’t, and now you’re paying the price, you goddamn idiot. I will shit fury all"
            " over you and you will drown in it. You’re fucking dead, kiddo.")
        print("Run: Navy Seal Copypasta")

    #Fist me daddy
    @commands.command()
    async def daddy(self):
        """Fist me Daddy."""
        await self.bot.say("iM LITEralLY CRyiNG FIST ME DADDY oMG im screaming tHere is no depth to my personality")
        print("Run: Daddy")

    #another fucking daddie thing
    @commands.command()
    async def cummies(self):
        """You want some?"""
        await self.bot.say("Just me and my 💕daddy💕, hanging out I got pretty hungry🍆 so I started to pout 😞 He asked if I was down ⬇for something yummy 😍🍆 and I asked what and he said he'd give me his 💦cummies!💦 Yeah! Yeah!💕💦 I drink them!💦 I slurp them!💦 I swallow them whole💦 😍 It makes 💘daddy💘 😊happy😊 so it's my only goal... 💕💦😫Harder daddy! Harder daddy! 😫💦💕 1 cummy💦, 2 cummy💦💦, 3 cummy💦💦💦, 4💦💦💦💦 I'm 💘daddy's💘 👑princess 👑but I'm also a whore! 💟 He makes me feel squishy💗!He makes me feel good💜! 💘💘💘He makes me feel everything a little should!~ 💘💘💘 👑💦💘Wa-What!💘💦👑")
        print("Run: Cummies")

def setup(bot):
    bot.add_cog(Copypasta(bot))