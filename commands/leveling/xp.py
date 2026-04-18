import discord
from discord import app_commands
from discord.ext import commands
from utils.json_manager import load_json, save_json
from utils.helpers import check_permissions
from config import LEVELS_FILE

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="xp", description="Manage XP 🌟")
    @app_commands.describe(action="add, remove, or set")
    async def xp(self, interaction: discord.Interaction, action: str, user: discord.Member, amount: int):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_roles"): return
        levels = load_json(LEVELS_FILE)
        u_data = levels.setdefault(str(interaction.guild_id), {}).setdefault(str(user.id), {"level": 0, "messages": 0})
        if action == "add": u_data["level"] += amount
        elif action == "remove": u_data["level"] = max(0, u_data["level"] - amount)
        elif action == "set": u_data["level"] = amount
        save_json(LEVELS_FILE, levels)
        await interaction.followup.send(f"✅ Set {user.mention} level to **{u_data['level']}**", ephemeral=False)

async def setup(bot):
    await bot.add_cog(XP(bot))
