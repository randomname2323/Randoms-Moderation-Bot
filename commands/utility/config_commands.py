import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from utils.json_manager import load_json, save_json
from utils.helpers import check_permissions
from config import ANTISWEAR_FILE, ANTISPAM_FILE, AUTOROLES_FILE

class ConfigCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="antiswear", description="Antiswear toggle 🚫")
    async def antiswear(self, interaction: discord.Interaction, enabled: bool):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_messages"): return
        config = load_json(ANTISWEAR_FILE)
        config[str(interaction.guild_id)] = {"enabled": enabled, "action": "delete", "warning_message": "Watch your language!"}
        save_json(ANTISWEAR_FILE, config)
        await interaction.followup.send(f"✅ Antiswear {'enabled' if enabled else 'disabled'}", ephemeral=False)

    @app_commands.command(name="antispam", description="Antispam toggle 🛡️")
    async def antispam(self, interaction: discord.Interaction, enabled: bool):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_messages"): return
        config = load_json(ANTISPAM_FILE)
        config[str(interaction.guild_id)] = {"enabled": enabled, "threshold": 5, "window_seconds": 10, "action": "delete", "warning_message": "Stop spamming!"}
        save_json(ANTISPAM_FILE, config)
        await interaction.followup.send(f"✅ Antispam {'enabled' if enabled else 'disabled'}", ephemeral=False)

    @app_commands.command(name="sync", description="🔄 Sync slash commands")
    async def sync(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "administrator"): return
        try:
            await self.bot.tree.sync()
            await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send("✅ Bot synchronized globally and locally! Restart your Discord app to see changes.")
        except Exception as e:
            await interaction.followup.send(f"❌ Synchronisation failed: {e}")

    @app_commands.command(name="autorole_setup", description="🤖 Setup automatic roles")
    async def autorole_setup(self, interaction: discord.Interaction, enabled: bool, role: discord.Role = None):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_guild"): return
        config = load_json(AUTOROLES_FILE)
        config[str(interaction.guild_id)] = {"enabled": enabled, "role_id": str(role.id) if role else None}
        save_json(AUTOROLES_FILE, config)
        role_mention = role.mention if role else "None"
        await interaction.followup.send(f"✅ Autorole {'enabled' if enabled else 'disabled'} (Role: {role_mention})")

    @app_commands.command(name="joinfilter_setup", description="🛡️ Setup join filters")
    async def joinfilter_setup(self, interaction: discord.Interaction, enabled: bool, min_age_days: int = 1, no_avatar: bool = False):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_guild"): return
        config = load_json(FILTER_JOIN_BOT_FILE)
        config[str(interaction.guild_id)] = {"enabled": enabled, "min_age_days": min_age_days, "no_avatar": no_avatar}
        save_json(FILTER_JOIN_BOT_FILE, config)
        await interaction.followup.send(f"✅ Join Filter {'enabled' if enabled else 'disabled'} (Min Age: {min_age_days}d, No Avatar: {no_avatar})")

async def setup(bot):
    await bot.add_cog(ConfigCommands(bot))
