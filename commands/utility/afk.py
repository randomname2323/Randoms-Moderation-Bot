import discord
from discord import app_commands
from discord.ext import commands
from utils.json_manager import read_data, write_data
from utils.helpers import dm_the_user
from config import afk_json

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="afk", description="🌙 Set AFK status")
    async def afk(self, inter: discord.Interaction, status: str = "AFK"):
        await inter.response.defer(ephemeral=False)
        afk_db = read_data(afk_json)
        afk_db.setdefault(str(inter.guild_id), {})[str(inter.user.id)] = {'status': status}
        write_data(afk_json, afk_db)
        await dm_the_user(inter.user, "AFK Set", inter.guild, status)
        await inter.followup.send(f"🌙 AFK status set: **{status}**")

async def setup(bot):
    await bot.add_cog(AFK(bot))
