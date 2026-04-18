import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="🎲 Roll a dice with animation")
    async def roll(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🎲 Dice Roll", description="Rolling...", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)
        
        dice_frames = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        for _ in range(3):
            for face in random.sample(dice_frames, 3):
                embed.description = f"**{face}** . . ."
                await interaction.edit_original_response(embed=embed)
                await asyncio.sleep(0.3)

        result = random.randint(1, 6)
        face = dice_frames[result-1]
        
        embed.title = "🎲 Result"
        embed.description = f"You rolled a **{result}** {face}!"
        embed.color = discord.Color.green()
        await interaction.edit_original_response(embed=embed)

async def setup(bot):
    await bot.add_cog(Roll(bot))
