import discord
from discord import app_commands
from discord.ext import commands
from utils.json_manager import load_json, save_json
from utils.helpers import check_permissions, send_action_dm
from config import WARNINGS_FILE

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="warn", description="⚠️ Warn a member")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_messages"): return
        warnings = load_json(WARNINGS_FILE)
        user_warnings = warnings.setdefault(str(interaction.guild_id), {}).setdefault(str(member.id), [])
        user_warnings.append({'reason': reason or "No reason provided", 'timestamp': discord.utils.utcnow().timestamp()})
        count = len(user_warnings)
        await send_action_dm(member, "Warned", interaction.guild, reason, warning_count=count)
        if count >= 3:
            await member.ban(reason="3 warnings")
            await interaction.followup.send(f"🔨 {member.mention} was banned for 3 warnings.", ephemeral=False)
        else:
            await interaction.followup.send(f"⚠️ {member.mention} was warned ({count}/3)", ephemeral=False)
        save_json(WARNINGS_FILE, warnings)

    @app_commands.command(name="unwarn", description="🔄 Remove a warning")
    async def unwarn(self, interaction: discord.Interaction, member: discord.Member, warning_id: int):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_messages"): return
        warnings = load_json(WARNINGS_FILE)
        user_warnings = warnings.get(str(interaction.guild_id), {}).get(str(member.id), [])
        if 0 <= warning_id < len(user_warnings):
            user_warnings.pop(warning_id)
            save_json(WARNINGS_FILE, warnings)
            await interaction.followup.send(f"✅ Removed warning {warning_id} from {member.mention}", ephemeral=False)
        else:
            await interaction.followup.send("❌ Invalid warning ID!", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Warn(bot))
