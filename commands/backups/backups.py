import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import logging
import asyncio
from utils.json_manager import save_json, load_json
from utils.helpers import check_permissions
from config import BACKUPS_DIR

logger = logging.getLogger(__name__)

class ConfirmLoadView(discord.ui.View):
    def __init__(self, interaction, name, parent_cog):
        super().__init__(timeout=60)
        self.interaction = interaction
        self.name = name
        self.parent_cog = parent_cog
        self.confirmed = False

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction.user.id:
            return await interaction.response.send_message("❌ Not for you!", ephemeral=True)
        
        self.confirmed = True
        self.stop()
        await interaction.response.edit_message(content="🔄 Backup loading confirmed! Loading server in progress...", view=None)
        await self.parent_cog.execute_nuclear_restore(self.interaction, self.name)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(content="❌ Loading cancelled.", view=None)

class Backups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user_backup_path(self, guild_id, user_id):
        return os.path.join(BACKUPS_DIR, str(guild_id), str(user_id))

    @app_commands.command(name="backup_create", description="💾 Create a backup")
    @app_commands.describe(name="Name for backup")
    async def backup_create(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer(ephemeral=False)
        if not await check_permissions(interaction, "administrator"): return
        
        guild = interaction.guild
        data = {
            "name": guild.name,
            "created_by": interaction.user.name,
            "user_id": interaction.user.id,
            "roles": [],
            "categories": [],
            "channels": []
        }

        for role in reversed(guild.roles):
            if not role.is_default() and not role.managed:
                data["roles"].append({
                    "name": role.name,
                    "color": role.color.value,
                    "permissions": role.permissions.value,
                    "hoist": role.hoist,
                    "mentionable": role.mentionable
                })

        for cat in guild.categories:
            data["categories"].append({"name": cat.name, "id": cat.id})

        for channel in guild.channels:
            if isinstance(channel, discord.CategoryChannel): continue
            data["channels"].append({
                "name": channel.name,
                "type": str(channel.type),
                "category": channel.category.name if channel.category else None,
                "topic": getattr(channel, 'topic', None),
                "nsfw": getattr(channel, 'nsfw', False)
            })

        user_path = self.get_user_backup_path(guild.id, interaction.user.id)
        os.makedirs(user_path, exist_ok=True)
        file_path = os.path.join(user_path, f"{name}.json")
        save_json(file_path, data)
        
        await interaction.followup.send(f"✅ Backup **{name}**  created successfully!")

    @app_commands.command(name="backup_load", description="☢️ Wipe server and load backup")
    @app_commands.describe(name="Name of backup to load")
    async def backup_load(self, interaction: discord.Interaction, name: str):
        if not await check_permissions(interaction, "administrator"): 
            return await interaction.response.send_message("❌ Admin only!", ephemeral=True)

        user_path = self.get_user_backup_path(interaction.guild_id, interaction.user.id)
        file_path = os.path.join(user_path, f"{name}.json")
        
        if not os.path.exists(file_path):
            return await interaction.response.send_message("❌ Backup not found!", ephemeral=True)

        view = ConfirmLoadView(interaction, name, self)
        await interaction.response.send_message(
            content=f"🚨 **CAUTION**: This will **DELETE EVERYTHING** in the server and replace it with backup **{name}**. Are you absolutely sure?", 
            view=view
        )

    async def execute_nuclear_restore(self, interaction: discord.Interaction, name: str):
        user_path = self.get_user_backup_path(interaction.guild_id, interaction.user.id)
        file_path = os.path.join(user_path, f"{name}.json")
        data = load_json(file_path)
        guild = interaction.guild

        for channel in guild.channels:
            try:
                if channel.id != interaction.channel_id:
                    await channel.delete()
            except: pass

        for role in guild.roles:
            if not role.is_default() and not role.managed and role.position < guild.me.top_role.position:
                try:
                    await role.delete()
                except: pass

        for r_data in data.get("roles", []):
            try:
                await guild.create_role(
                    name=r_data["name"],
                    color=discord.Color(r_data["color"]),
                    permissions=discord.Permissions(r_data["permissions"]),
                    hoist=r_data["hoist"],
                    mentionable=r_data["mentionable"]
                )
            except: pass

        cat_map = {}
        for c_data in data.get("categories", []):
            try:
                new_cat = await guild.create_category(name=c_data["name"])
                cat_map[c_data["name"]] = new_cat
            except: pass

        first_text_channel = None
        for ch_data in data.get("channels", []):
            try:
                cat = cat_map.get(ch_data["category"])
                if ch_data["type"] == "text":
                    new_ch = await guild.create_text_channel(name=ch_data["name"], category=cat, topic=ch_data["topic"], nsfw=ch_data["nsfw"])
                    if not first_text_channel: first_text_channel = new_ch
                elif ch_data["type"] == "voice":
                    await guild.create_voice_channel(name=ch_data["name"], category=cat)
            except: pass

        try:
            old_channel = guild.get_channel(interaction.channel_id)
            if old_channel:
                await old_channel.delete()
        except: pass

        if first_text_channel:
            await first_text_channel.send(f"✅ Backup **{name}** loaded successfully.")

    @app_commands.command(name="backup_list", description="📋 List your server backups")
    async def backup_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        user_path = self.get_user_backup_path(interaction.guild_id, interaction.user.id)
        
        if not os.path.exists(user_path) or not os.listdir(user_path):
            await interaction.followup.send("📋 You haven't created any backups yet!")
            return

        backups = [f.replace(".json", "") for f in os.listdir(user_path) if f.endswith(".json")]
        embed = discord.Embed(title=f"📋 {interaction.user.name}'s Backups", color=discord.Color.blue())
        embed.description = "\n".join([f"• `{b}`" for b in backups])
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Backups(bot))
