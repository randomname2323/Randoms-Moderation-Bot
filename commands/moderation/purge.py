import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import check_permissions

class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="purge", description="Purge messages 🧹")
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_messages"): return
        await interaction.channel.purge(limit=amount)
        await interaction.channel.send(f"🧹 Purged {amount} messages.", delete_after=5)

    @app_commands.command(name="clean", description="Clean bot messages 🧼")
    async def clean(self, interaction: discord.Interaction, amount: int = 100):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_messages"): return
        deleted = await interaction.channel.purge(limit=amount, check=lambda m: m.author == self.bot.user)
        await interaction.channel.send(f"🧼 Cleaned {len(deleted)} bot messages.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Purge(bot))
