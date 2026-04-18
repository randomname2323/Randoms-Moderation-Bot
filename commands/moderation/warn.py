import discord
from discord import app_commands
from discord.ext import commands
from utils.json_manager import read_data, write_data
from utils.helpers import can_do, dm_the_user
from config import warns_json

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="⚠️ Warn a mem")
    async def warn(self, inter: discord.Interaction, mem: discord.Member, why: str = None):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_messages"): return
        warnings = read_data(warns_json)
        user_warnings = warnings.setdefault(str(inter.guild_id), {}).setdefault(str(mem.id), [])
        user_warnings.append({'why': why or "No why provided", 'timestamp': discord.utils.utcnow().timestamp()})
        count = len(user_warnings)
        await dm_the_user(mem, "Warned", inter.guild, why, warn_cnt=count)
        if count >= 3:
            await mem.ban(why="3 warnings")
            await inter.followup.send(f"🔨 {mem.mention} was banned for 3 warnings.", ephemeral=False)
        else:
            await inter.followup.send(f"⚠️ {mem.mention} was warned ({count}/3)", ephemeral=False)
        write_data(warns_json, warnings)

    @app_commands.command(name="unwarn", description="🔄 Remove a warning")
    async def unwarn(self, inter: discord.Interaction, mem: discord.Member, w_id: int):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_messages"): return
        warnings = read_data(warns_json)
        user_warnings = warnings.get(str(inter.guild_id), {}).get(str(mem.id), [])
        if 0 <= w_id < len(user_warnings):
            user_warnings.pop(w_id)
            write_data(warns_json, warnings)
            await inter.followup.send(f"✅ Removed warning {w_id} from {mem.mention}", ephemeral=False)
        else:
            await inter.followup.send("❌ Invalid warning ID!", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Warn(bot))
