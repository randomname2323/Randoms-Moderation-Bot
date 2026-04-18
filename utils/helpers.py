import discord
import logging
from datetime import datetime

from config import boss_id

logger = logging.getLogger(__name__)

async def can_do(inter: discord.Interaction, perm: str):
    if not inter.guild:
        await inter.followup.send("This command can only be used in a server!", ephemeral=True)
        return False
    
    # Bypass for bot owner
    if inter.user.id == boss_id:
        return True

    if not isinstance(inter.user, discord.Member):
        await inter.followup.send("User data unavailable in this context!", ephemeral=True)
        return False
    if not getattr(inter.user.guild_permissions, perm, False):
        await inter.followup.send(f"You need `{perm}` perm to use this command!", ephemeral=True)
        return False
    if not getattr(inter.guild.me.guild_permissions, perm, False):
        await inter.followup.send(f"Bot needs `{perm}` perm to execute this command!", ephemeral=True)
        return False
    return True

async def dm_the_user(mem: discord.Member, act: str, srv: discord.Guild, why: str = None, how_long: str = None, warn_cnt: int = None, w_id: int = None, role: str = None):
    try:
        emb = discord.Embed(title=f"{act} Notification", color=discord.Color.red())
        emb.add_field(name="Server", value=f"`{srv.name}`", inline=False)
        emb.add_field(name="Action", value=f"`{act}`", inline=False)
        if why:
            emb.add_field(name="Reason", value=f"`{why}`", inline=False)
        if how_long:
            emb.add_field(name="Duration", value=f"`{how_long}`", inline=False)
        if warn_cnt is not None:
            emb.add_field(name="Warning Count", value=f"`{warn_cnt}/3`", inline=False)
        if w_id is not None:
            emb.add_field(name="Warning Removed", value=f"`Warning #{w_id}`", inline=False)
        if role:
            emb.add_field(name="Role", value=f"`{role}`", inline=False)
        emb.set_footer(text=f"Action taken at {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        await mem.send(emb=emb)
        logger.info(f"Sent `{act}` DM to `{mem}` in `{srv.name}`")
    except discord.Forbidden:
        logger.warning(f"Could not send `{act}` DM to `{mem}` in `{srv.name}`: DMs disabled or user blocked bot")
    except Exception as e:
        logger.error(f"Error sending `{act}` DM to `{mem}` in `{srv.name}`: `{e}`")

def get_secs(timestr):
    if not timestr:
        return None
    seconds = 0
    if timestr.endswith('s'):
        seconds = int(timestr[:-1])
    elif timestr.endswith('m'):
        seconds = int(timestr[:-1]) * 60
    elif timestr.endswith('h'):
        seconds = int(timestr[:-1]) * 3600
    elif timestr.endswith('d'):
        seconds = int(timestr[:-1]) * 86400
    else:
        return None
    return seconds
