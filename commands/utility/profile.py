import discord
from discord import app_commands
from discord.ext import commands

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="🖼️ Get a user's avatar")
    async def avatar(self, inter: discord.Interaction, user: discord.Member = None):
        await inter.response.defer(ephemeral=False)
        user = user or inter.user
        emb = discord.Embed(title=f"🖼️ {user.name}'s Avatar", color=discord.Color.blue())
        emb.set_image(url=user.display_avatar.url)
        await inter.followup.send(emb=emb, ephemeral=False)

    @app_commands.command(name="servericon", description="🖼️ Get server icon")
    async def servericon(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=False)
        if not inter.guild.icon:
            await inter.followup.send("❌ No icon set!", ephemeral=False)
            return
        emb = discord.Embed(title=f"🖼️ {inter.guild.name} Icon", color=discord.Color.blue())
        emb.set_image(url=inter.guild.icon.url)
        await inter.followup.send(emb=emb, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Profile(bot))
