import discord
from discord.ext import commands
import logging
from datetime import datetime, UTC, timedelta
from collections import defaultdict, deque
from utils.json_manager import read_data, write_data, get_words
from config import (
    antiswear_json, antispam_json, invites_json, afk_json, 
    levels_json, autoroles_json, botfilter_json, 
    bad_words_txt
)
import re

logger = logging.getLogger(__name__)
INVITE_REGEX = re.compile(r'(?:https?:\/\/)?discord(?:app)?\.com\/invite\/([a-zA-Z0-9-]+)')

class EventHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.antispam_history = defaultdict(deque)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"Bot logged in as {self.bot.user.name}")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot or not msg.guild:
            return
        
        sid = str(msg.guild.id)
        uid = str(msg.author.id)

        swear_settings = read_data(antiswear_json)
        if sid in swear_settings and swear_settings[sid]["enabled"]:
            text_low = msg.content.lower()
            no_no_list = get_words(bad_words_txt)
            if any(word in text_low for word in no_no_list):
                try: 
                    await msg.delete()
                    await msg.channel.send(f"🚫 {msg.author.mention}, {swear_settings[sid]['warning_message']}", delete_after=5)
                    return
                except: pass

        spam_settings = read_data(antispam_json)
        if sid in spam_settings and spam_settings[sid]["enabled"]:
            hist = self.antispam_history[uid]
            hist.append(msg.created_at)
            
            window = spam_settings[sid].get("window_seconds", 10)
            limit = spam_settings[sid].get("limit", 5)
            
            window = timedelta(seconds=window)
            last_few = [m for m in hist if msg.created_at - m < window]
            
            if len(last_few) > limit:
                try:
                    await msg.delete()
                    await msg.channel.send(f"🛡️ {msg.author.mention}, {spam_settings[sid]['warning_message']}", delete_after=5)
                    return
                except: pass

        if INVITE_REGEX.search(msg.content):
            if (sid in swear_settings and swear_settings[sid]["enabled"]) or \
               (sid in spam_settings and spam_settings[sid]["enabled"]):
                try:
                    await msg.delete()
                    await msg.channel.send(f"🔗 {msg.author.mention}, Invite links are not allowed here!", delete_after=5)
                    return
                except: pass

        afk_db = read_data(afk_json)
        if sid in afk_db and uid in afk_db[sid]:
            del afk_db[sid][uid]
            write_data(afk_json, afk_db)
            await msg.channel.send(f"👋 Welcome back {msg.author.mention}, I've removed your AFK status.", delete_after=5)

        for mentioned in msg.mentions:
            m_id = str(mentioned.id)
            if sid in afk_db and m_id in afk_db[sid]:
                await msg.channel.send(f"🌙 {mentioned.name} is currently AFK: **{afk_db[sid][m_id]['status']}**")

        if not msg.content.startswith('/'):
            levels = read_data(levels_json)
            usr_dat = levels.setdefault(sid, {}).setdefault(uid, {"messages": 0, "level": 0})
            usr_dat["messages"] += 1
            if usr_dat["messages"] % 100 == 0:
                usr_dat["level"] += 1
                await msg.channel.send(f"⭐ {msg.author.mention} reached level **{usr_dat['level']}**!")
            write_data(levels_json, levels)

    @commands.Cog.listener()
    async def on_member_join(self, mem):
        sid = str(mem.guild.id)
        
        join_settings = read_data(botfilter_json)
        if sid in join_settings and join_settings[sid].get("enabled", False):
            min_days = join_settings[sid].get("min_age_days", 1)
            acc_age = (datetime.now(UTC) - mem.created_at).days
            
            if acc_age < min_days or (join_settings[sid].get("no_avatar", False) and not mem.avatar):
                try:
                    await mem.send(f"❌ You were kicked from **{mem.guild.name}** because your account is too new or lacks an avatar.")
                    await mem.kick(why="Join Filter: Account too new / No avatar")
                    return
                except: pass

        config = read_data(autoroles_json)
        if sid in config and config[sid].get("enabled", False):
            role_id = config[sid].get("role_id")
            if role_id:
                role = mem.guild.get_role(int(role_id))
                if role: 
                    try: await mem.add_roles(role)
                    except: pass


    @commands.Cog.listener()
    async def on_message_delete(self, msg):
        if not msg.guild or msg.author.bot: return

async def setup(bot):
    await bot.add_cog(EventHandler(bot))
