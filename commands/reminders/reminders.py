import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
from utils.json_manager import read_data, write_data
from config import reminders_json

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="remindme", description="⏰ Set a reminder")
    async def remindme(self, inter: discord.Interaction, time: str, reminder: str):
        await inter.response.defer(ephemeral=False)
        seconds = 0
        if time.endswith('s'): seconds = int(time[:-1])
        elif time.endswith('m'): seconds = int(time[:-1]) * 60
        elif time.endswith('h'): seconds = int(time[:-1]) * 3600
        elif time.endswith('d'): seconds = int(time[:-1]) * 86400
        else:
            await inter.followup.send("❌ Invalid time format!", ephemeral=False)
            return

        expiry = discord.utils.utcnow() + timedelta(seconds=seconds)
        reminders = read_data(reminders_json)
        r_list = reminders.setdefault(str(inter.guild_id), {}).setdefault(str(inter.user.id), {})
        r_list[str(len(r_list))] = {'reminder': reminder, 'expiry': expiry.isoformat()}
        write_data(reminders_json, reminders)
        await inter.followup.send(f"✅ Reminder set for <t:{int(expiry.timestamp())}:R>", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Reminders(bot))
