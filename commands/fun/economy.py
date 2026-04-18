import discord
from discord import app_commands
from discord.ext import commands
import random
from datetime import datetime, timedelta, UTC
from utils.json_manager import load_json, save_json
from utils.helpers import check_permissions

ECONOMY_FILE = "database/economy.json"

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    def get_data(self, guild_id, user_id):
        data = load_json(ECONOMY_FILE)
        g_id = str(guild_id)
        u_id = str(user_id)
        if g_id not in data: data[g_id] = {}
        if u_id not in data[g_id]: data[g_id][u_id] = {"balance": 0, "last_daily": None, "last_work": None}
        return data, g_id, u_id

    @app_commands.command(name="balance", description="💰 Check your bank account")
    async def balance(self, interaction: discord.Interaction, user: discord.Member = None):
        await interaction.response.defer(ephemeral=False)
        user = user or interaction.user
        data, g_id, u_id = self.get_data(interaction.guild_id, user.id)
        bal = data[g_id][u_id]["balance"]
        
        embed = discord.Embed(title=f"💰 {user.name}'s Balance", color=discord.Color.green())
        embed.add_field(name="Wallet", value=f"`${bal:,}`")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="daily", description="🎁 Claim your daily reward")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        data, g_id, u_id = self.get_data(interaction.guild_id, interaction.user.id)
        
        now = datetime.now(UTC)
        last = data[g_id][u_id].get("last_daily")
        
        if last:
            last_dt = datetime.fromisoformat(last)
            if now - last_dt < timedelta(days=1):
                next_daily = last_dt + timedelta(days=1)
                return await interaction.followup.send(f"❌ You already claimed your daily! Try again <t:{int(next_daily.timestamp())}:R>")

        amount = random.randint(500, 2000)
        data[g_id][u_id]["balance"] += amount
        data[g_id][u_id]["last_daily"] = now.isoformat()
        save_json(ECONOMY_FILE, data)
        
        await interaction.followup.send(f"🎁 You claimed your daily reward of **${amount:,}**!")

    @app_commands.command(name="work", description="💼 Work for some cash")
    async def work(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        data, g_id, u_id = self.get_data(interaction.guild_id, interaction.user.id)
        
        now = datetime.now(UTC)
        last = data[g_id][u_id].get("last_work")
        
        if last:
            last_dt = datetime.fromisoformat(last)
            if now - last_dt < timedelta(hours=1):
                next_work = last_dt + timedelta(hours=1)
                return await interaction.followup.send(f"❌ You are tired! Work again <t:{int(next_work.timestamp())}:R>")

        jobs = ["Developer", "Designer", "Streamer", "Miner", "Chef", "Doctor"]
        job = random.choice(jobs)
        amount = random.randint(100, 500)
        
        data[g_id][u_id]["balance"] += amount
        data[g_id][u_id]["last_work"] = now.isoformat()
        save_json(ECONOMY_FILE, data)
        
        await interaction.followup.send(f"💼 You worked as a **{job}** and earned **${amount:,}**!")

    @app_commands.command(name="gamble", description="🎰 Risk it all!")
    async def gamble(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=False)
        if amount <= 0: return await interaction.followup.send("❌ Enter a valid amount!")
        
        data, g_id, u_id = self.get_data(interaction.guild_id, interaction.user.id)
        if data[g_id][u_id]["balance"] < amount:
            return await interaction.followup.send("❌ You don't have enough money!")

        win = random.choice([True, False])
        if win:
            data[g_id][u_id]["balance"] += amount
            msg = f"🎰 **JACKPOT!** You won **${amount:,}**!"
            color = discord.Color.green()
        else:
            data[g_id][u_id]["balance"] -= amount
            msg = f"📉 **L** - You lost **${amount:,}**... Better luck next time."
            color = discord.Color.red()
            
        save_json(ECONOMY_FILE, data)
        embed = discord.Embed(title="🎰 Gambling Den", description=msg, color=color)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="pay", description="💸 Send money to a friend")
    async def pay(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        await interaction.response.defer(ephemeral=False)
        if amount <= 0 or user.id == interaction.user.id:
            return await interaction.followup.send("❌ Invalid transaction!")
        
        data, g_id, u_id = self.get_data(interaction.guild_id, interaction.user.id)
        target_data, _, t_id = self.get_data(interaction.guild_id, user.id)
        
        if data[g_id][u_id]["balance"] < amount:
            return await interaction.followup.send("❌ Insufficient funds!")

        data[g_id][u_id]["balance"] -= amount
        data[g_id][t_id]["balance"] += amount
        save_json(ECONOMY_FILE, data)
        
        await interaction.followup.send(f"💸 Sent **${amount:,}** to {user.mention}!")

async def setup(bot):
    await bot.add_cog(Economy(bot))
