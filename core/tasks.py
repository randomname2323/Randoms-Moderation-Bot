import discord
from discord.ext import commands, tasks
import logging
from datetime import datetime, UTC
from dateutil.parser import parse
from utils.json_manager import read_data, write_data
from config import bans_json, mutes_json, reminders_json

logger = logging.getLogger(__name__)

class TaskHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.clean_stuff.start()
        self.remind_check.start()

    def cog_unload(self):
        self.clean_stuff.cancel()
        self.remind_check.cancel()

    @tasks.loop(minutes=1)
    async def clean_stuff(self):
        now = discord.utils.utcnow()
        tempbans = read_data(bans_json)
        tempmutes = read_data(mutes_json)
        
        for sid, bans in list(tempbans.items()):
            for uid, data in list(bans.items()):
                if now >= parse(data['expiry']):
                    srv = self.bot.get_guild(int(sid))
                    if srv:
                        try:
                            await srv.unban(discord.Object(id=int(uid)))
                            del tempbans[sid][uid]
                        except: pass
        write_data(bans_json, tempbans)

        for sid, mutes in list(tempmutes.items()):
            for uid, data in list(mutes.items()):
                if now >= parse(data['expiry']):
                    srv = self.bot.get_guild(int(sid))
                    mem = srv.get_member(int(uid)) if srv else None
                    if mem:
                        try:
                            await mem.timeout(None)
                            del tempmutes[sid][uid]
                        except: pass
        write_data(mutes_json, tempmutes)

    @tasks.loop(seconds=30)
    async def remind_check(self):
        now = discord.utils.utcnow()
        reminders = read_data(reminders_json)
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
        write_data(reminders_json, reminders)

async def setup(bot):
    await bot.add_cog(TaskHandler(bot))
