import discord
import logging
from datetime import datetime

from config import ALLOWED_USER_ID

logger = logging.getLogger(__name__)

async def check_permissions(interaction: discord.Interaction, permission: str):
    if not interaction.guild:
        await interaction.followup.send("This command can only be used in a server!", ephemeral=True)
        return False
    
    # Bypass for bot owner
    if interaction.user.id == ALLOWED_USER_ID:
        return True

    if not isinstance(interaction.user, discord.Member):
        await interaction.followup.send("User data unavailable in this context!", ephemeral=True)
        return False
    if not getattr(interaction.user.guild_permissions, permission, False):
        await interaction.followup.send(f"You need `{permission}` permission to use this command!", ephemeral=True)
        return False
    if not getattr(interaction.guild.me.guild_permissions, permission, False):
        await interaction.followup.send(f"Bot needs `{permission}` permission to execute this command!", ephemeral=True)
        return False
    return True

async def send_action_dm(member: discord.Member, action: str, guild: discord.Guild, reason: str = None, duration: str = None, warning_count: int = None, warning_id: int = None, role: str = None):
    try:
        embed = discord.Embed(title=f"{action} Notification", color=discord.Color.red())
        embed.add_field(name="Server", value=f"`{guild.name}`", inline=False)
        embed.add_field(name="Action", value=f"`{action}`", inline=False)
        if reason:
            embed.add_field(name="Reason", value=f"`{reason}`", inline=False)
        if duration:
            embed.add_field(name="Duration", value=f"`{duration}`", inline=False)
        if warning_count is not None:
            embed.add_field(name="Warning Count", value=f"`{warning_count}/3`", inline=False)
        if warning_id is not None:
            embed.add_field(name="Warning Removed", value=f"`Warning #{warning_id}`", inline=False)
        if role:
            embed.add_field(name="Role", value=f"`{role}`", inline=False)
        embed.set_footer(text=f"Action taken at {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        await member.send(embed=embed)
        logger.info(f"Sent `{action}` DM to `{member}` in `{guild.name}`")
    except discord.Forbidden:
        logger.warning(f"Could not send `{action}` DM to `{member}` in `{guild.name}`: DMs disabled or user blocked bot")
    except Exception as e:
        logger.error(f"Error sending `{action}` DM to `{member}` in `{guild.name}`: `{e}`")

def parse_duration(duration_str):
    if not duration_str:
        return None
    seconds = 0
    if duration_str.endswith('s'):
        seconds = int(duration_str[:-1])
    elif duration_str.endswith('m'):
        seconds = int(duration_str[:-1]) * 60
    elif duration_str.endswith('h'):
        seconds = int(duration_str[:-1]) * 3600
    elif duration_str.endswith('d'):
        seconds = int(duration_str[:-1]) * 86400
    else:
        return None
    return seconds
