import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.helpers import can_do, dm_the_user
logger = logging.getLogger(__name__)

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="👢 Kick a mem")
    @app_commands.describe(mem="Member to kick", why="Reason for kicking")
    async def kick(self, inter: discord.Interaction, mem: discord.Member, why: str = None):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "kick_members"): return 
        try:
            await dm_the_user(mem, "Kicked", inter.guild, why)
            await mem.kick(why=why)
            emb = discord.Embed(title="👢 Member Kicked", description=f"{mem.mention} has been kicked", color=discord.Color.blue())
            await inter.followup.send(emb=emb, ephemeral=False)
        except Exception as e:
            await inter.followup.send(f"❌ Error: {e}", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Kick(bot))
