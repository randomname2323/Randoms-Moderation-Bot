import discord
from discord import app_commands
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta, UTC
from utils.json_manager import load_json, save_json
from utils.helpers import check_permissions
from config import GIVEAWAYS_FILE, LEVELS_FILE

class GiveawayEntry(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="Enter Giveaway", style=discord.ButtonStyle.primary, emoji="🎉", custom_id="giveaway_entry_btn")
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_json(GIVEAWAYS_FILE)
        g_id = str(self.giveaway_id)
        
        if g_id not in data or data[g_id].get('ended', False):
            return await interaction.response.send_message("❌ This giveaway has already ended!", ephemeral=True)
        
        if interaction.user.id in data[g_id]['entrants']:
            return await interaction.response.send_message("❌ You are already in the giveaway!", ephemeral=True)

        req_role = data[g_id].get('required_role')
        if req_role:
            role = interaction.guild.get_role(int(req_role))
            if role and role not in interaction.user.roles:
                return await interaction.response.send_message(f"❌ You need the **{role.name}** role to enter!", ephemeral=True)

        min_lvl = data[g_id].get('min_level', 0)
        if min_lvl > 0:
            levels = load_json(LEVELS_FILE)
            u_lvl = levels.get(str(interaction.guild_id), {}).get(str(interaction.user.id), {}).get('level', 0)
            if u_lvl < min_lvl:
                return await interaction.response.send_message(f"❌ You need to be **Level {min_lvl}** to enter! (Your level: {u_lvl})", ephemeral=True)
            
        data[g_id]['entrants'].append(interaction.user.id)
        save_json(GIVEAWAYS_FILE, data)
        
        embed = interaction.message.embeds[0]
        embed.set_footer(text=f"Entries: {len(data[g_id]['entrants'])} | ID: {g_id}")
        await interaction.response.edit_message(embed=embed)
        await interaction.followup.send("✅ You have successfully entered!", ephemeral=True)

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    def cog_unload(self):
        self.check_giveaways.cancel()

    @tasks.loop(seconds=10)
    async def check_giveaways(self):
        data = load_json(GIVEAWAYS_FILE)
        now = datetime.now(UTC).timestamp()
        
        changed = False
        for g_id, info in list(data.items()):
            if not info.get('ended', False) and now >= info['end_time']:
                await self.finish_giveaway(g_id, info)
                info['ended'] = True
                changed = True
        
        if changed: save_json(GIVEAWAYS_FILE, data)

    async def finish_giveaway(self, g_id, info):
        channel = self.bot.get_channel(info['channel_id'])
        if not channel: return
        try: message = await channel.fetch_message(info['message_id'])
        except: return

        entrants = info['entrants']
        winners_count = info['winners']
        prize = info['prize']

        if not entrants:
            embed = discord.Embed(title="🎉 Giveaway Ended", description=f"Prize: **{prize}**\nWinner: **No entries found.**", color=discord.Color.red())
            await message.edit(embed=embed, view=None)
            return

        winners = random.sample(entrants, min(len(entrants), winners_count))
        mentions = ", ".join([f"<@{w}>" for w in winners])

        embed = discord.Embed(
            title="🎊 Giveaway Result!",
            description=f"Prize: **{prize}**\nWinners: {mentions}\nHost: <@{info['host_id']}>",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Total Entries: {len(entrants)}")
        await message.edit(embed=embed, view=None)
        await channel.send(f"Congratulations {mentions}! You won **{prize}**! 🏆", reference=message)

    @app_commands.command(name="giveaway_start", description="🎉 Start a giveaway")
    async def giveaway_start(self, interaction: discord.Interaction, duration: str, winners: int, prize: str, min_level: int = 0, required_role: discord.Role = None):
        if not await check_permissions(interaction, "manage_guild"): 
            return await interaction.response.send_message("❌ Admin only!", ephemeral=True)

        seconds = 0
        if duration.endswith('s'): seconds = int(duration[:-1])
        elif duration.endswith('m'): seconds = int(duration[:-1]) * 60
        elif duration.endswith('h'): seconds = int(duration[:-1]) * 3600
        elif duration.endswith('d'): seconds = int(duration[:-1]) * 86400
        else: return await interaction.response.send_message("❌ Format: 10s, 5m, 1h, 1d", ephemeral=True)

        end_ts = int((datetime.now(UTC) + timedelta(seconds=seconds)).timestamp())
        embed = discord.Embed(
            title="🎁 NEW GIVEAWAY 🎁",
            description=f"Prize: **{prize}**\nWinners: `{winners}`\nEnds in: <t:{end_ts}:R>\nHost: {interaction.user.mention}",
            color=discord.Color.blue()
        )
        if min_level > 0: embed.add_field(name="⭐ Required Level", value=f"Level `{min_level}`+", inline=True)
        if required_role: embed.add_field(name="🛡️ Required Role", value=required_role.mention, inline=True)
        embed.set_footer(text="Entries: 0")

        await interaction.response.send_message("✅ Giveaway started!", ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        
        data = load_json(GIVEAWAYS_FILE)
        data[str(msg.id)] = {
            'prize': prize, 'winners': winners, 'end_time': end_ts,
            'channel_id': interaction.channel_id, 'message_id': msg.id,
            'host_id': interaction.user.id, 'entrants': [], 'ended': False,
            'min_level': min_level, 'required_role': str(required_role.id) if required_role else None
        }
        save_json(GIVEAWAYS_FILE, data)
        await msg.edit(view=GiveawayEntry(msg.id))

    @app_commands.command(name="giveaway_reroll", description="🎲 Reroll a new winner")
    async def giveaway_reroll(self, interaction: discord.Interaction, message_id: str):
        if not await check_permissions(interaction, "manage_guild"): return
        data = load_json(GIVEAWAYS_FILE)
        if message_id not in data:
            return await interaction.response.send_message("❌ Giveaway not found in history!", ephemeral=True)
        
        info = data[message_id]
        if not info['entrants']:
            return await interaction.response.send_message("❌ No entrants to reroll from!", ephemeral=True)

        winner = random.choice(info['entrants'])
        await interaction.response.send_message(f"🎲 **Reroll**: The new winner for **{info['prize']}** is <@{winner}>! Congratulations! 🎉")

    @app_commands.command(name="giveaway_end", description="⏹️ Force end a giveaway")
    async def giveaway_end(self, interaction: discord.Interaction, message_id: str):
        if not await check_permissions(interaction, "manage_guild"): return
        data = load_json(GIVEAWAYS_FILE)
        if message_id not in data or data[message_id]['ended']:
            return await interaction.response.send_message("❌ Active giveaway not found!", ephemeral=True)
        
        await self.finish_giveaway(message_id, data[message_id])
        data[message_id]['ended'] = True
        save_json(GIVEAWAYS_FILE, data)
        await interaction.response.send_message("✅ Giveaway ended manually.")

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
