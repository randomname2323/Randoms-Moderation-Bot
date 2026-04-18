import discord
from discord import app_commands
from discord.ext import commands
import logging
from utils.helpers import check_permissions, send_action_dm
logger = logging.getLogger(__name__)

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="👢 Kick a member")
    @app_commands.describe(member="Member to kick", reason="Reason for kicking")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "kick_members"): return 
        try:
            await send_action_dm(member, "Kicked", interaction.guild, reason)
            await member.kick(reason=reason)
            embed = discord.Embed(title="👢 Member Kicked", description=f"{member.mention} has been kicked", color=discord.Color.blue())
            await interaction.followup.send(embed=embed, ephemeral=False)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Kick(bot))
