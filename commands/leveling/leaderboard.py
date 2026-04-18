import discord
from discord import app_commands
from discord.ext import commands
from utils.json_manager import load_json
from config import LEVELS_FILE

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Leaderboard 📊")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        levels = load_json(LEVELS_FILE)
        guild_data = levels.get(str(interaction.guild_id), {})
        if not guild_data:
            await interaction.followup.send("🏆 No rankings yet!", ephemeral=False)
            return
        sorted_users = sorted(guild_data.items(), key=lambda x: x[1]['level'], reverse=True)[:10]
        desc = "\n".join([f"**{i+1}.** <@{u_id}> - Level {d['level']}" for i, (u_id, d) in enumerate(sorted_users)])
        embed = discord.Embed(title=f"🏆 {interaction.guild.name} Leaderboard", description=desc, color=discord.Color.gold())
        await interaction.followup.send(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
