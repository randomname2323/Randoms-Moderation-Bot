import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import check_permissions

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="slowmode", description="⏲️ Set slowmode")
    async def slowmode(self, interaction: discord.Interaction, delay: int, channel: discord.TextChannel = None):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_channels"): return
        channel = channel or interaction.channel
        await channel.edit(slowmode_delay=delay)
        await interaction.followup.send(f"⏲️ Slowmode set to {delay}s in {channel.mention}.", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Slowmode(bot))
