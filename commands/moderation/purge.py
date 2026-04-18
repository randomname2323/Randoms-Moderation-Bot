import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import can_do

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="purge", description="Purge messages 🧹")
    async def purge(self, inter: discord.Interaction, cash: int):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_messages"): return
        await inter.channel.purge(limit=cash)
        await inter.channel.send(f"🧹 Purged {cash} messages.", delete_after=5)

    @app_commands.command(name="clean", description="Clean bot messages 🧼")
    async def clean(self, inter: discord.Interaction, cash: int = 100):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_messages"): return
        deleted = await inter.channel.purge(limit=cash, check=lambda m: m.author == self.bot.user)
        await inter.channel.send(f"🧼 Cleaned {len(deleted)} bot messages.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Purge(bot))
