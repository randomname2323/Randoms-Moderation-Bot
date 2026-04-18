import discord
from discord import app_commands
from discord.ext import commands
from utils.json_manager import read_data
from config import levels_json

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="level", description="Check your level 🏆")
    async def level(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=False)
        levels = read_data(levels_json)
        data = levels.get(str(inter.guild_id), {}).get(str(inter.user.id), {"level": 0, "messages": 0})
        await inter.followup.send(f"📊 {inter.user.mention}, you are level **{data['level']}** ({data['messages']} messages).", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Level(bot))
