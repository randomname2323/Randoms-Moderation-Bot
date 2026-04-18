import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import can_do

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="slowmode", description="⏲️ Set slowmode")
    async def slowmode(self, inter: discord.Interaction, delay: int, chan: discord.TextChannel = None):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_channels"): return
        chan = chan or inter.channel
        await chan.edit(slowmode_delay=delay)
        await inter.followup.send(f"⏲️ Slowmode set to {delay}s in {chan.mention}.", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Slowmode(bot))
