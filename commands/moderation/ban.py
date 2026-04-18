import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.helpers import check_permissions, send_action_dm
logger = logging.getLogger(__name__)

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="🔨 Ban a member")
    @app_commands.describe(member="Member to ban", reason="Reason for banning", days="Days of messages to delete (0-7)")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None, days: int = 0):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "ban_members"): return
        try:
            await send_action_dm(member, "Banned", interaction.guild, reason)
            await member.ban(reason=reason, delete_message_days=days)
            embed = discord.Embed(title="🔨 Member Banned", description=f"{member.mention} has been banned", color=discord.Color.blue())
            await interaction.followup.send(embed=embed, ephemeral=False)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Ban(bot))
