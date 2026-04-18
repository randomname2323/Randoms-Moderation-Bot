import discord
from discord import app_commands
from discord.ext import commands
from utils.json_manager import read_data
from config import levels_json

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Leaderboard 📊")
    async def leaderboard(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=False)
        levels = read_data(levels_json)
        srv_dat = levels.get(str(inter.guild_id), {})
        if not srv_dat:
            await inter.followup.send("🏆 No rankings yet!", ephemeral=False)
            return
        sorted_users = sorted(srv_dat.items(), key=lambda x: x[1]['level'], reverse=True)[:10]
        desc = "\n".join([f"**{i+1}.** <@{u_id}> - Level {d['level']}" for i, (u_id, d) in enumerate(sorted_users)])
        emb = discord.Embed(title=f"🏆 {inter.guild.name} Leaderboard", description=desc, color=discord.Color.gold())
        await inter.followup.send(emb=emb, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
