import discord
from discord.ext import commands
import logging
from datetime import datetime, UTC, timedelta
from collections import defaultdict, deque
from utils.json_manager import load_json, save_json, load_bad_words
from config import (
    ANTISWEAR_FILE, ANTISPAM_FILE, INVITES_FILE, AFK_FILE, 
    LEVELS_FILE, AUTOROLES_FILE, FILTER_JOIN_BOT_FILE, 
    BAD_WORDS_FILE
)
import re

logger = logging.getLogger(__name__)
INVITE_REGEX = re.compile(r'(?:https?:\/\/)?discord(?:app)?\.com\/invite\/([a-zA-Z0-9-]+)')

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.antispam_history = defaultdict(deque)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"Bot logged in as {self.bot.user.name}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        
        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

        antiswear_config = load_json(ANTISWEAR_FILE)
        if guild_id in antiswear_config and antiswear_config[guild_id]["enabled"]:
            content_lower = message.content.lower()
            bad_words = load_bad_words(BAD_WORDS_FILE)
            if any(word in content_lower for word in bad_words):
                try: 
                    await message.delete()
                    await message.channel.send(f"🚫 {message.author.mention}, {antiswear_config[guild_id]['warning_message']}", delete_after=5)
                    return
                except: pass

        antispam_config = load_json(ANTISPAM_FILE)
        if guild_id in antispam_config and antispam_config[guild_id]["enabled"]:
            history = self.antispam_history[user_id]
            history.append(message.created_at)
            
            window_sec = antispam_config[guild_id].get("window_seconds", 10)
            threshold = antispam_config[guild_id].get("threshold", 5)
            
            window = timedelta(seconds=window_sec)
            recent = [m for m in history if message.created_at - m < window]
            
            if len(recent) > threshold:
                try:
                    await message.delete()
                    await message.channel.send(f"🛡️ {message.author.mention}, {antispam_config[guild_id]['warning_message']}", delete_after=5)
                    return
                except: pass

        if INVITE_REGEX.search(message.content):
            if (guild_id in antiswear_config and antiswear_config[guild_id]["enabled"]) or \
               (guild_id in antispam_config and antispam_config[guild_id]["enabled"]):
                try:
                    await message.delete()
                    await message.channel.send(f"🔗 {message.author.mention}, Invite links are not allowed here!", delete_after=5)
                    return
                except: pass

        afk_data = load_json(AFK_FILE)
        if guild_id in afk_data and user_id in afk_data[guild_id]:
            del afk_data[guild_id][user_id]
            save_json(AFK_FILE, afk_data)
            await message.channel.send(f"👋 Welcome back {message.author.mention}, I've removed your AFK status.", delete_after=5)

        for mentioned in message.mentions:
            m_id = str(mentioned.id)
            if guild_id in afk_data and m_id in afk_data[guild_id]:
                await message.channel.send(f"🌙 {mentioned.name} is currently AFK: **{afk_data[guild_id][m_id]['status']}**")

        if not message.content.startswith('/'):
            levels = load_json(LEVELS_FILE)
            user_data = levels.setdefault(guild_id, {}).setdefault(user_id, {"messages": 0, "level": 0})
            user_data["messages"] += 1
            if user_data["messages"] % 100 == 0:
                user_data["level"] += 1
                await message.channel.send(f"⭐ {message.author.mention} reached level **{user_data['level']}**!")
            save_json(LEVELS_FILE, levels)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        
        filter_config = load_json(FILTER_JOIN_BOT_FILE)
        if guild_id in filter_config and filter_config[guild_id].get("enabled", False):
            age_threshold = filter_config[guild_id].get("min_age_days", 1)
            account_age = (datetime.now(UTC) - member.created_at).days
            
            if account_age < age_threshold or (filter_config[guild_id].get("no_avatar", False) and not member.avatar):
                try:
                    await member.send(f"❌ You were kicked from **{member.guild.name}** because your account is too new or lacks an avatar.")
                    await member.kick(reason="Join Filter: Account too new / No avatar")
                    return
                except: pass

        config = load_json(AUTOROLES_FILE)
        if guild_id in config and config[guild_id].get("enabled", False):
            role_id = config[guild_id].get("role_id")
            if role_id:
                role = member.guild.get_role(int(role_id))
                if role: 
                    try: await member.add_roles(role)
                    except: pass


    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.author.bot: return

async def setup(bot):
    await bot.add_cog(Events(bot))
