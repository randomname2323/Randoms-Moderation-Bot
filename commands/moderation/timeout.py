import discord
from discord import app_commands
from discord.ext import commands
import logging
from datetime import timedelta
from utils.helpers import check_permissions, send_action_dm, parse_duration
from utils.json_manager import load_json, save_json
from config import TEMPMUTES_FILE

logger = logging.getLogger(__name__)

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="timeout", description="⏳ Timeout a member for a duration")
    @app_commands.describe(member="Member to timeout", duration="Duration (e.g., 1h, 30m)", reason="Reason for timeout")
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = None):
        await interaction.response.defer(ephemeral=False)
        await self.apply_timeout(interaction, member, duration, reason)

    @app_commands.command(name="tempmute", description="⏳ Mute a member for a duration (alias for timeout)")
    async def tempmute(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = None):
        await interaction.response.defer(ephemeral=False)
        await self.apply_timeout(interaction, member, duration, reason)

    async def apply_timeout(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = None):
        if not await check_permissions(interaction, "moderate_members"): return
        seconds = parse_duration(duration)
        if seconds is None:
            await interaction.followup.send("❌ Invalid duration format!", ephemeral=False)
            return
        expiry = discord.utils.utcnow() + timedelta(seconds=seconds)
        try:
            await send_action_dm(member, "Timed Out", interaction.guild, reason, duration)
            await member.timeout(expiry, reason=reason)
            tempmutes = load_json(TEMPMUTES_FILE)
            tempmutes.setdefault(str(interaction.guild_id), {})[str(member.id)] = {'expiry': expiry.isoformat(), 'reason': reason}
            save_json(TEMPMUTES_FILE, tempmutes)
            await interaction.followup.send(f"✅ Timed out {member.mention} until <t:{int(expiry.timestamp())}:F>", ephemeral=False)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Timeout(bot))
