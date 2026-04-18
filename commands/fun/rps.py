import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

class RPSView(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.primary, emoji="🪨")
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play(interaction, "Rock")

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.primary, emoji="📜")
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play(interaction, "Paper")

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.primary, emoji="✂️")
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play(interaction, "Scissors")

    async def play(self, interaction: discord.Interaction, user_choice):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ Start your own game!", ephemeral=True)
        
        self.stop()
        bot_choice = random.choice(["Rock", "Paper", "Scissors"])
        
        embed = discord.Embed(title="🎮 Rock Paper Scissors", description="Let's see...", color=discord.Color.blue())
        await interaction.response.edit_message(embed=embed, view=None)
        
        frames = ["🪨 Rock!", "📜 Paper!", "✂️ Scissors!", "🔥 GO!"]
        for frame in frames:
            embed.description = f"**{frame}**"
            await interaction.edit_original_response(embed=embed)
            await asyncio.sleep(0.5)

        result = ""
        color = discord.Color.blue()
        if user_choice == bot_choice:
            result = "It's a **Tie**! 🤝"
        elif (user_choice == "Rock" and bot_choice == "Scissors") or \
             (user_choice == "Paper" and bot_choice == "Rock") or \
             (user_choice == "Scissors" and bot_choice == "Paper"):
            result = f"**You Win!** 🏆\n`{user_choice}` beats `{bot_choice}`"
            color = discord.Color.green()
        else:
            result = f"**I Win!** 🤖\n`{bot_choice}` beats `{user_choice}`"
            color = discord.Color.red()

        embed.title = "🎮 Game Results"
        embed.description = result
        embed.color = color
        await interaction.edit_original_response(embed=embed)

class RPS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rps", description="🕹️ Play a cool game of Rock Paper Scissors")
    async def rps(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎮 Rock Paper Scissors",
            description="Choose your weapon! Will you beat me?",
            color=discord.Color.blue()
        )
        view = RPSView(interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(RPS(bot))
