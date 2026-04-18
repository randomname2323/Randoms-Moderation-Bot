import discord
from discord import app_commands
from discord.ext import commands
from utils.json_manager import load_json, save_json
from utils.helpers import send_action_dm
from config import AFK_FILE

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="afk", description="🌙 Set AFK status")
    async def afk(self, interaction: discord.Interaction, status: str = "AFK"):
        await interaction.response.defer(ephemeral=False)
        afk_data = load_json(AFK_FILE)
        afk_data.setdefault(str(interaction.guild_id), {})[str(interaction.user.id)] = {'status': status}
        save_json(AFK_FILE, afk_data)
        await send_action_dm(interaction.user, "AFK Set", interaction.guild, status)
        await interaction.followup.send(f"🌙 AFK status set: **{status}**")

async def setup(bot):
    await bot.add_cog(AFK(bot))
