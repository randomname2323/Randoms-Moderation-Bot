import discord
from discord import app_commands
from discord.ext import commands
from utils.json_manager import read_data, write_data
from utils.helpers import can_do
from config import levels_json

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="xp", description="Manage XP 🌟")
    @app_commands.describe(act="add, remove, or set")
    async def xp(self, inter: discord.Interaction, act: str, user: discord.Member, cash: int):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_roles"): return
        levels = read_data(levels_json)
        u_data = levels.setdefault(str(inter.guild_id), {}).setdefault(str(user.id), {"level": 0, "messages": 0})
        if act == "add": u_data["level"] += cash
        elif act == "remove": u_data["level"] = max(0, u_data["level"] - cash)
        elif act == "set": u_data["level"] = cash
        write_data(levels_json, levels)
        await inter.followup.send(f"✅ Set {user.mention} level to **{u_data['level']}**", ephemeral=False)

async def setup(bot):
    await bot.add_cog(XP(bot))
