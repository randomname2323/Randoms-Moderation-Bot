import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from utils.json_manager import read_data, write_data
from utils.helpers import can_do
from config import antiswear_json, antispam_json, autoroles_json

class ConfigCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="antiswear", description="Antiswear toggle 🚫")
    async def antiswear(self, inter: discord.Interaction, enabled: bool):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_messages"): return
        config = read_data(antiswear_json)
        config[str(inter.guild_id)] = {"enabled": enabled, "act": "delete", "warning_message": "Watch your language!"}
        write_data(antiswear_json, config)
        await inter.followup.send(f"✅ Antiswear {'enabled' if enabled else 'disabled'}", ephemeral=False)

    @app_commands.command(name="antispam", description="Antispam toggle 🛡️")
    async def antispam(self, inter: discord.Interaction, enabled: bool):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_messages"): return
        config = read_data(antispam_json)
        config[str(inter.guild_id)] = {"enabled": enabled, "limit": 5, "window_seconds": 10, "act": "delete", "warning_message": "Stop spamming!"}
        write_data(antispam_json, config)
        await inter.followup.send(f"✅ Antispam {'enabled' if enabled else 'disabled'}", ephemeral=False)

    @app_commands.command(name="sync", description="🔄 Sync slash commands")
    async def sync(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "administrator"): return
        try:
            await self.bot.tree.sync()
            await self.bot.tree.sync(srv=inter.guild)
            await inter.followup.send("✅ Bot synchronized globally and locally! Restart your Discord app to see changes.")
        except Exception as e:
            await inter.followup.send(f"❌ Synchronisation failed: {e}")

    @app_commands.command(name="autorole_setup", description="🤖 Setup automatic roles")
    async def autorole_setup(self, inter: discord.Interaction, enabled: bool, role: discord.Role = None):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_guild"): return
        config = read_data(autoroles_json)
        config[str(inter.guild_id)] = {"enabled": enabled, "role_id": str(role.id) if role else None}
        write_data(autoroles_json, config)
        role_mention = role.mention if role else "None"
        await inter.followup.send(f"✅ Autorole {'enabled' if enabled else 'disabled'} (Role: {role_mention})")

    @app_commands.command(name="joinfilter_setup", description="🛡️ Setup join filters")
    async def joinfilter_setup(self, inter: discord.Interaction, enabled: bool, min_age_days: int = 1, no_avatar: bool = False):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_guild"): return
        config = read_data(botfilter_json)
        config[str(inter.guild_id)] = {"enabled": enabled, "min_age_days": min_age_days, "no_avatar": no_avatar}
        write_data(botfilter_json, config)
        await inter.followup.send(f"✅ Join Filter {'enabled' if enabled else 'disabled'} (Min Age: {min_age_days}d, No Avatar: {no_avatar})")

async def setup(bot):
    await bot.add_cog(ConfigCommands(bot))
