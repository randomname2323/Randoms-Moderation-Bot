import discord
from discord import app_commands
from discord.ext import commands
from utils.json_manager import load_json
from config import LEVELS_FILE

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="level", description="Check your level 🏆")
    async def level(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        levels = load_json(LEVELS_FILE)
        data = levels.get(str(interaction.guild_id), {}).get(str(interaction.user.id), {"level": 0, "messages": 0})
        await interaction.followup.send(f"📊 {interaction.user.mention}, you are level **{data['level']}** ({data['messages']} messages).", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Level(bot))
