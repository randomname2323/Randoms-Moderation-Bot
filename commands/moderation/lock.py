import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import check_permissions

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="channel_lock", description="Lock channel 🔒")
    async def channel_lock(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_channels"): return
        channel = channel or interaction.channel
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.followup.send(f"🔒 {channel.mention} locked.", ephemeral=False)

    @app_commands.command(name="channel_unlock", description="Unlock channel 🔓")
    async def channel_unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_channels"): return
        channel = channel or interaction.channel
        await channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.followup.send(f"🔓 {channel.mention} unlocked.", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Lock(bot))
