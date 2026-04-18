import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from utils.json_manager import load_json, save_json
from config import REMINDERS_FILE

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="remindme", description="⏰ Set a reminder")
    async def remindme(self, interaction: discord.Interaction, time: str, reminder: str):
        await interaction.response.defer(ephemeral=False)
        seconds = 0
        if time.endswith('s'): seconds = int(time[:-1])
        elif time.endswith('m'): seconds = int(time[:-1]) * 60
        elif time.endswith('h'): seconds = int(time[:-1]) * 3600
        elif time.endswith('d'): seconds = int(time[:-1]) * 86400
        else:
            await interaction.followup.send("❌ Invalid time format!", ephemeral=False)
            return

        expiry = discord.utils.utcnow() + timedelta(seconds=seconds)
        reminders = load_json(REMINDERS_FILE)
        r_list = reminders.setdefault(str(interaction.guild_id), {}).setdefault(str(interaction.user.id), {})
        r_list[str(len(r_list))] = {'reminder': reminder, 'expiry': expiry.isoformat()}
        save_json(REMINDERS_FILE, reminders)
        await interaction.followup.send(f"✅ Reminder set for <t:{int(expiry.timestamp())}:R>", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Reminders(bot))
