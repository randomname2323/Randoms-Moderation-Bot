import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta, UTC
from utils.json_manager import read_data, write_data
from utils.helpers import can_do
from config import giveaways_json, levels_json

class GiveawayEntry(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="Enter Giveaway", style=discord.ButtonStyle.primary, emoji="🎉", custom_id="giveaway_entry_btn")
    async def enter(self, inter: discord.Interaction, button: discord.ui.Button):
        data = read_data(giveaways_json)
        g_id = str(self.giveaway_id)
        
        if g_id not in data or data[g_id].get('ended', False):
            return await inter.response.send_message("❌ This giveaway has already ended!", ephemeral=True)
        
        if inter.user.id in data[g_id]['entrants']:
            return await inter.response.send_message("❌ You are already in the giveaway!", ephemeral=True)

        req_role = data[g_id].get('required_role')
        if req_role:
            role = inter.guild.get_role(int(req_role))
            if role and role not in inter.user.roles:
                return await inter.response.send_message(f"❌ You need the **{role.name}** role to enter!", ephemeral=True)

        min_lvl = data[g_id].get('min_level', 0)
        if min_lvl > 0:
            levels = read_data(levels_json)
            u_lvl = levels.get(str(inter.guild_id), {}).get(str(inter.user.id), {}).get('level', 0)
            if u_lvl < min_lvl:
                return await inter.response.send_message(f"❌ You need to be **Level {min_lvl}** to enter! (Your level: {u_lvl})", ephemeral=True)
            
        data[g_id]['entrants'].append(inter.user.id)
        write_data(giveaways_json, data)
        
        emb = inter.msg.embeds[0]
        emb.set_footer(text=f"Entries: {len(data[g_id]['entrants'])} | ID: {g_id}")
        await inter.response.edit_message(emb=emb)
        await inter.followup.send("✅ You have successfully entered!", ephemeral=True)

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        data = read_data(giveaways_json)
        now = datetime.now(UTC).timestamp()
        
        changed = False
        for g_id, info in list(data.items()):
            if not info.get('ended', False) and now >= info['end_time']:
                await self.finish_giveaway(g_id, info)
                info['ended'] = True
                changed = True
        
        if changed: write_data(giveaways_json, data)

    async def finish_giveaway(self, g_id, info):
        chan = self.bot.get_channel(info['channel_id'])
        if not chan: return
        try: msg = await chan.fetch_message(info['message_id'])
        except: return

        entrants = info['entrants']
        winners_count = info['winners']
        prize = info['prize']

        if not entrants:
            emb = discord.Embed(title="🎉 Giveaway Ended", description=f"Prize: **{prize}**\nWinner: **No entries found.**", color=discord.Color.red())
            await msg.edit(emb=emb, view=None)
            return

        winners = random.sample(entrants, min(len(entrants), winners_count))
        mentions = ", ".join([f"<@{w}>" for w in winners])

        emb = discord.Embed(
            title="🎊 Giveaway Result!",
            description=f"Prize: **{prize}**\nWinners: {mentions}\nHost: <@{info['host_id']}>",
            color=discord.Color.gold()
        )
        emb.set_footer(text=f"Total Entries: {len(entrants)}")
        await msg.edit(emb=emb, view=None)
        await chan.send(f"Congratulations {mentions}! You won **{prize}**! 🏆", reference=msg)

    @app_commands.command(name="giveaway_start", description="🎉 Start a giveaway")
    async def giveaway_start(self, inter: discord.Interaction, how_long: str, winners: int, prize: str, min_level: int = 0, required_role: discord.Role = None):
        if not await can_do(inter, "manage_guild"): 
            return await inter.response.send_message("❌ Admin only!", ephemeral=True)

        seconds = 0
        if how_long.endswith('s'): seconds = int(how_long[:-1])
        elif how_long.endswith('m'): seconds = int(how_long[:-1]) * 60
        elif how_long.endswith('h'): seconds = int(how_long[:-1]) * 3600
        elif how_long.endswith('d'): seconds = int(how_long[:-1]) * 86400
        else: return await inter.response.send_message("❌ Format: 10s, 5m, 1h, 1d", ephemeral=True)

        end_ts = int((datetime.now(UTC) + timedelta(seconds=seconds)).timestamp())
        emb = discord.Embed(
            title="🎁 NEW GIVEAWAY 🎁",
            description=f"Prize: **{prize}**\nWinners: `{winners}`\nEnds in: <t:{end_ts}:R>\nHost: {inter.user.mention}",
            color=discord.Color.blue()
        )
        if min_level > 0: emb.add_field(name="⭐ Required Level", value=f"Level `{min_level}`+", inline=True)
        if required_role: emb.add_field(name="🛡️ Required Role", value=required_role.mention, inline=True)
        emb.set_footer(text="Entries: 0")

        await inter.response.send_message("✅ Giveaway started!", ephemeral=True)
        msg = await inter.channel.send(emb=emb)
        
        data = read_data(giveaways_json)
        data[str(msg.id)] = {
            'prize': prize, 'winners': winners, 'end_time': end_ts,
            'channel_id': inter.channel_id, 'message_id': msg.id,
            'host_id': inter.user.id, 'entrants': [], 'ended': False,
            'min_level': min_level, 'required_role': str(required_role.id) if required_role else None
        }
        write_data(giveaways_json, data)
        await msg.edit(view=GiveawayEntry(msg.id))

    @app_commands.command(name="giveaway_reroll", description="🎲 Reroll a new winner")
    async def giveaway_reroll(self, inter: discord.Interaction, message_id: str):
        if not await can_do(inter, "manage_guild"): return
        data = read_data(giveaways_json)
        if message_id not in data:
            return await inter.response.send_message("❌ Giveaway not found in hist!", ephemeral=True)
        
        info = data[message_id]
        if not info['entrants']:
            return await inter.response.send_message("❌ No entrants to reroll from!", ephemeral=True)

        winner = random.choice(info['entrants'])
        await inter.response.send_message(f"🎲 **Reroll**: The new winner for **{info['prize']}** is <@{winner}>! Congratulations! 🎉")

    @app_commands.command(name="giveaway_end", description="⏹️ Force end a giveaway")
    async def giveaway_end(self, inter: discord.Interaction, message_id: str):
        if not await can_do(inter, "manage_guild"): return
        data = read_data(giveaways_json)
        if message_id not in data or data[message_id]['ended']:
            return await inter.response.send_message("❌ Active giveaway not found!", ephemeral=True)
        
        await self.finish_giveaway(message_id, data[message_id])
        data[message_id]['ended'] = True
        write_data(giveaways_json, data)
        await inter.response.send_message("✅ Giveaway ended manually.")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
