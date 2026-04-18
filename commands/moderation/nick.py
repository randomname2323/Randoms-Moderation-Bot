import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import check_permissions

class Nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setnick", description="🏷️ Change nickname")
    async def setnick(self, interaction: discord.Interaction, member: discord.Member, nickname: str):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "manage_nicknames"): return
        await member.edit(nick=nickname)
        await interaction.followup.send(f"✅ Changed nickname for {member.mention} to **{nickname}**", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Nick(bot))
