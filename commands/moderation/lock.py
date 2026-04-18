import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import can_do

class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="channel_lock", description="Lock chan 🔒")
    async def channel_lock(self, inter: discord.Interaction, chan: discord.TextChannel = None):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_channels"): return
        chan = chan or inter.channel
        await chan.set_permissions(inter.guild.default_role, send_messages=False)
        await inter.followup.send(f"🔒 {chan.mention} locked.", ephemeral=False)

    @app_commands.command(name="channel_unlock", description="Unlock chan 🔓")
    async def channel_unlock(self, inter: discord.Interaction, chan: discord.TextChannel = None):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_channels"): return
        chan = chan or inter.channel
        await chan.set_permissions(inter.guild.default_role, send_messages=True)
        await inter.followup.send(f"🔓 {chan.mention} unlocked.", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Lock(bot))
