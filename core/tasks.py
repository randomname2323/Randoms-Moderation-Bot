import discord
from discord.ext import commands, tasks
import logging
from datetime import datetime, UTC
from dateutil.parser import parse
from utils.json_manager import load_json, save_json
from config import TEMPBANS_FILE, TEMPMUTES_FILE, REMINDERS_FILE

logger = logging.getLogger(__name__)

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cleanup_slots.start()
        self.check_reminders.start()

    def cog_unload(self):
        self.cleanup_slots.cancel()
        self.check_reminders.cancel()

    @tasks.loop(minutes=1)
    async def cleanup_slots(self):
        now = discord.utils.utcnow()
        tempbans = load_json(TEMPBANS_FILE)
        tempmutes = load_json(TEMPMUTES_FILE)
        
        for guild_id, bans in list(tempbans.items()):
            for user_id, data in list(bans.items()):
                if now >= parse(data['expiry']):
                    guild = self.bot.get_guild(int(guild_id))
                    if guild:
                        try:
                            await guild.unban(discord.Object(id=int(user_id)))
                            del tempbans[guild_id][user_id]
                        except: pass
        save_json(TEMPBANS_FILE, tempbans)

        for guild_id, mutes in list(tempmutes.items()):
            for user_id, data in list(mutes.items()):
                if now >= parse(data['expiry']):
                    guild = self.bot.get_guild(int(guild_id))
                    member = guild.get_member(int(user_id)) if guild else None
                    if member:
                        try:
                            await member.timeout(None)
                            del tempmutes[guild_id][user_id]
                        except: pass
        save_json(TEMPMUTES_FILE, tempmutes)

    @tasks.loop(seconds=30)
    async def check_reminders(self):
        now = discord.utils.utcnow()
        reminders = load_json(REMINDERS_FILE)
        for g_id, g_reminders in list(reminders.items()):
            for u_id, u_reminders in list(g_reminders.items()):
                for r_id, data in list(u_reminders.items()):
                    if now >= datetime.fromisoformat(data['expiry']):
                        user = await self.bot.fetch_user(int(u_id))
                        if user:
                            try:
                                await user.send(f"⏰ **Reminder**: {data['reminder']}")
                            except: pass
                        del reminders[g_id][u_id][r_id]
        save_json(REMINDERS_FILE, reminders)

async def setup(bot):
    await bot.add_cog(Tasks(bot))
