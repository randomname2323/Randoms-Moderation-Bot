import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime, timedelta, UTC
from utils.json_manager import read_data, write_data
from utils.helpers import can_do

ECONOMY_FILE = "database/economy.json"

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cds = {}

    def grab_stuff(self, sid, uid):
        data = read_data(ECONOMY_FILE)
        g_id = str(sid)
        u_id = str(uid)
        if g_id not in data: data[g_id] = {}
        if u_id not in data[g_id]: data[g_id][u_id] = {"money": 0, "daily_t": None, "work_t": None}
        return data, g_id, u_id

    @app_commands.command(name="money", description="💰 Check your bank account")
    async def money(self, inter: discord.Interaction, user: discord.Member = None):
        await inter.response.defer(ephemeral=False)
        user = user or inter.user
        data, g_id, u_id = self.grab_stuff(inter.guild_id, user.id)
        bal = data[g_id][u_id]["money"]
        
        emb = discord.Embed(title=f"💰 {user.name}'s Balance", color=discord.Color.green())
        emb.add_field(name="Wallet", value=f"`${bal:,}`")
        await inter.followup.send(emb=emb)

    @app_commands.command(name="daily", description="🎁 Claim your daily reward")
    async def daily(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=False)
        data, g_id, u_id = self.grab_stuff(inter.guild_id, inter.user.id)
        
        now = datetime.now(UTC)
        last = data[g_id][u_id].get("daily_t")
        
        if last:
            last_dt = datetime.fromisoformat(last)
            if now - last_dt < timedelta(days=1):
                can_daily = last_dt + timedelta(days=1)
                return await inter.followup.send(f"❌ You already claimed your daily! Try again <t:{int(can_daily.timestamp())}:R>")

        cash = random.randint(500, 2000)
        data[g_id][u_id]["money"] += cash
        data[g_id][u_id]["daily_t"] = now.isoformat()
        write_data(ECONOMY_FILE, data)
        
        await inter.followup.send(f"🎁 You claimed your daily reward of **${cash:,}**!")

    @app_commands.command(name="work", description="💼 Work for some cash")
    async def work(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=False)
        data, g_id, u_id = self.grab_stuff(inter.guild_id, inter.user.id)
        
        now = datetime.now(UTC)
        last = data[g_id][u_id].get("work_t")
        
        if last:
            last_dt = datetime.fromisoformat(last)
            if now - last_dt < timedelta(hours=1):
                can_work = last_dt + timedelta(hours=1)
                return await inter.followup.send(f"❌ You are tired! Work again <t:{int(can_work.timestamp())}:R>")

        work_list = ["Developer", "Designer", "Streamer", "Miner", "Chef", "Doctor"]
        the_job = random.choice(work_list)
        cash = random.randint(100, 500)
        
        data[g_id][u_id]["money"] += cash
        data[g_id][u_id]["work_t"] = now.isoformat()
        write_data(ECONOMY_FILE, data)
        
        await inter.followup.send(f"💼 You worked as a **{the_job}** and earned **${cash:,}**!")

    @app_commands.command(name="gamble", description="🎰 Risk it all!")
    async def gamble(self, inter: discord.Interaction, cash: int):
        await inter.response.defer(ephemeral=False)
        if cash <= 0: return await inter.followup.send("❌ Enter a valid cash!")
        
        data, g_id, u_id = self.grab_stuff(inter.guild_id, inter.user.id)
        if data[g_id][u_id]["money"] < cash:
            return await inter.followup.send("❌ You don't have enough money!")

        win = random.choice([True, False])
        if win:
            data[g_id][u_id]["money"] += cash
            msg = f"🎰 **JACKPOT!** You won **${cash:,}**!"
            color = discord.Color.green()
        else:
            data[g_id][u_id]["money"] -= cash
            msg = f"📉 **L** - You lost **${cash:,}**... Better luck next time."
            color = discord.Color.red()
            
        write_data(ECONOMY_FILE, data)
        emb = discord.Embed(title="🎰 Gambling Den", description=msg, color=color)
        await inter.followup.send(emb=emb)

    @app_commands.command(name="pay", description="💸 Send money to a friend")
    async def pay(self, inter: discord.Interaction, user: discord.Member, cash: int):
        await inter.response.defer(ephemeral=False)
        if cash <= 0 or user.id == inter.user.id:
            return await inter.followup.send("❌ Invalid transaction!")
        
        data, g_id, u_id = self.grab_stuff(inter.guild_id, inter.user.id)
        trg_dat, _, t_id = self.grab_stuff(inter.guild_id, user.id)
        
        if data[g_id][u_id]["money"] < cash:
            return await inter.followup.send("❌ Insufficient funds!")

        data[g_id][u_id]["money"] -= cash
        data[g_id][t_id]["money"] += cash
        write_data(ECONOMY_FILE, data)
        
        await inter.followup.send(f"💸 Sent **${cash:,}** to {user.mention}!")

async def setup(bot):
    await bot.add_cog(Economy(bot))
