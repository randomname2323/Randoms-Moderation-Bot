import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, UTC

class Whois(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="whois", description="🕵️ Get user information")
    async def whois(self, inter: discord.Interaction, user: discord.Member = None):
        await inter.response.defer(ephemeral=False)
        user = user or inter.user
        emb = discord.Embed(title=f"🕵️ {user.name}'s Info", color=discord.Color.blue())
        emb.set_thumbnail(url=user.display_avatar.url)
        emb.add_field(name="ID", value=user.id, inline=True)
        emb.add_field(name="Joined Server", value=f"<t:{int(user.joined_at.timestamp())}:R>", inline=True)
        emb.add_field(name="Joined Discord", value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
        await inter.followup.send(emb=emb, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Whois(bot))
