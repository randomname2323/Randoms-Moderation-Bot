import discord
from discord import app_commands
from discord.ext import commands
from utils.helpers import can_do

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addrole", description="➕ Add a role to a mem")
    async def addrole(self, inter: discord.Interaction, user: discord.Member, role: discord.Role):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_roles"): return
        await user.add_roles(role)
        await inter.followup.send(f"✅ Added {role.name} to {user.mention}", ephemeral=False)

    @app_commands.command(name="removerole", description="➖ Remove a role from a mem")
    async def removerole(self, inter: discord.Interaction, user: discord.Member, role: discord.Role):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_roles"): return
        await user.remove_roles(role)
        await inter.followup.send(f"✅ Removed {role.name} from {user.mention}", ephemeral=False)

    @app_commands.command(name="rolename", description="✏️ Rename a role")
    async def rolename(self, inter: discord.Interaction, role: discord.Role, name: str):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "manage_roles"): return
        old_name = role.name
        await role.edit(name=name)
        await inter.followup.send(f"✅ Renamed role **{old_name}** to **{name}**", ephemeral=False)

async def setup(bot):
    await bot.add_cog(Roles(bot))
