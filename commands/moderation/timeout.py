import discord
from discord import app_commands
from discord.ext import commands
import logging
from datetime import timedelta
from utils.helpers import can_do, dm_the_user, get_secs
from utils.json_manager import read_data, write_data
from config import mutes_json

logger = logging.getLogger(__name__)

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="timeout", description="⏳ Timeout a mem for a how_long")
    @app_commands.describe(mem="Member to timeout", how_long="Duration (e.g., 1h, 30m)", why="Reason for timeout")
    async def timeout(self, inter: discord.Interaction, mem: discord.Member, how_long: str, why: str = None):
        await inter.response.defer(ephemeral=False)
        await self.apply_timeout(inter, mem, how_long, why)

    @app_commands.command(name="tempmute", description="⏳ Mute a mem for a how_long (alias for timeout)")
    async def tempmute(self, inter: discord.Interaction, mem: discord.Member, how_long: str, why: str = None):
        await inter.response.defer(ephemeral=False)
        await self.apply_timeout(inter, mem, how_long, why)

    async def apply_timeout(self, inter: discord.Interaction, mem: discord.Member, how_long: str, why: str = None):
        if not await can_do(inter, "moderate_members"): return
        seconds = get_secs(how_long)
        if seconds is None:
            await inter.followup.send("❌ Invalid how_long format!", ephemeral=False)
            return
        expiry = discord.utils.utcnow() + timedelta(seconds=seconds)
        try:
            await dm_the_user(mem, "Timed Out", inter.guild, why, how_long)
            await mem.timeout(expiry, why=why)
            tempmutes = read_data(mutes_json)
            tempmutes.setdefault(str(inter.guild_id), {})[str(mem.id)] = {'expiry': expiry.isoformat(), 'why': why}
            write_data(mutes_json, tempmutes)
            await inter.followup.send(f"✅ Timed out {mem.mention} until <t:{int(expiry.timestamp())}:F>", ephemeral=False)
        except Exception as e:
            await inter.followup.send(f"❌ Error: {e}", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Timeout(bot))
