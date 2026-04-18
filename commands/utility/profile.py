import discord
from discord import app_commands
from discord.ext import commands

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="🖼️ Get a user's avatar")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        await interaction.response.defer(ephemeral=False)
        user = user or interaction.user
        embed = discord.Embed(title=f"🖼️ {user.name}'s Avatar", color=discord.Color.blue())
        embed.set_image(url=user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=False)

    @app_commands.command(name="servericon", description="🖼️ Get server icon")
    async def servericon(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if not interaction.guild.icon:
            await interaction.followup.send("❌ No icon set!", ephemeral=False)
            return
        embed = discord.Embed(title=f"🖼️ {interaction.guild.name} Icon", color=discord.Color.blue())
        embed.set_image(url=interaction.guild.icon.url)
        await interaction.followup.send(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Profile(bot))
