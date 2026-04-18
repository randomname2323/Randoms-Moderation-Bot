import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import can_do

class Nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setnick", description="🏷️ Change nickname")
    async def setnick(self, inter: discord.Interaction, mem: discord.Member, nickname: str):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_nicknames"): return
        await mem.edit(nick=nickname)
        await inter.followup.send(f"✅ Changed nickname for {mem.mention} to **{nickname}**", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Nick(bot))
