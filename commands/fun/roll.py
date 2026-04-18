import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

class Roll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="🎲 Roll a dice with animation")
    async def roll(self, inter: discord.Interaction):
        emb = discord.Embed(title="🎲 Dice Roll", description="Rolling...", color=discord.Color.blue())
        await inter.response.send_message(emb=emb)
        
        dice_frames = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        for _ in range(3):
            for face in random.sample(dice_frames, 3):
                emb.description = f"**{face}** . . ."
                await inter.edit_original_response(emb=emb)
                await asyncio.sleep(0.3)

        result = random.randint(1, 6)
        face = dice_frames[result-1]
        
        emb.title = "🎲 Result"
        emb.description = f"You rolled a **{result}** {face}!"
        emb.color = discord.Color.green()
        await inter.edit_original_response(emb=emb)

async def setup(bot):
    await bot.add_cog(Roll(bot))
