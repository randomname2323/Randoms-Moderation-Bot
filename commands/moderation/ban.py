import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.helpers import can_do, dm_the_user
logger = logging.getLogger(__name__)

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="🔨 Ban a mem")
    @app_commands.describe(mem="Member to ban", why="Reason for banning", days="Days of messages to delete (0-7)")
    async def ban(self, inter: discord.Interaction, mem: discord.Member, why: str = None, days: int = 0):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "ban_members"): return
        try:
            await dm_the_user(mem, "Banned", inter.guild, why)
            await mem.ban(why=why, delete_message_days=days)
            emb = discord.Embed(title="🔨 Member Banned", description=f"{mem.mention} has been banned", color=discord.Color.blue())
            await inter.followup.send(emb=emb, ephemeral=False)
        except Exception as e:
            await inter.followup.send(f"❌ Error: {e}", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Ban(bot))
