import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import logging
import asyncio
from utils.json_manager import write_data, read_data
from utils.helpers import can_do
from config import backup_path

logger = logging.getLogger(__name__)

class ConfirmLoadView(discord.ui.View):
    def __init__(self, inter, name, parent_cog):
        super().__init__(timeout=60)
        self.inter = inter
        self.name = name
        self.parent_cog = parent_cog
        self.confirmed = False

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success, emoji="✅")
    async def confirm(self, inter: discord.Interaction, button: discord.ui.Button):
        if inter.user.id != self.inter.user.id:
            return await inter.response.send_message("❌ Not for you!", ephemeral=True)
        
        self.confirmed = True
        self.stop()
        await inter.response.edit_message(txt="🔄 Backup loading confirmed! Loading server in progress...", view=None)
        await self.parent_cog.execute_nuclear_restore(self.inter, self.name)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, inter: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await inter.response.edit_message(txt="❌ Loading cancelled.", view=None)

class Backups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def user_backup(self, sid, uid):
        return os.path.join(backup_path, str(sid), str(uid))

    @app_commands.command(name="backup_create", description="💾 Create a backup")
    @app_commands.describe(name="Name for backup")
    async def backup_create(self, inter: discord.Interaction, name: str):
        await inter.response.defer(ephemeral=False)
        if not await can_do(inter, "administrator"): return
        
        srv = inter.guild
        data = {
            "name": srv.name,
            "created_by": inter.user.name,
            "uid": inter.user.id,
            "roles": [],
            "categories": [],
            "channels": []
        }

        for role in reversed(srv.roles):
            if not role.is_default() and not role.managed:
                data["roles"].append({
                    "name": role.name,
                    "color": role.color.value,
                    "permissions": role.permissions.value,
                    "hoist": role.hoist,
                    "mentionable": role.mentionable
                })

        for cat in srv.categories:
            data["categories"].append({"name": cat.name, "id": cat.id})

        for chan in srv.channels:
            if isinstance(chan, discord.CategoryChannel): continue
            data["channels"].append({
                "name": chan.name,
                "type": str(chan.type),
                "category": chan.category.name if chan.category else None,
                "topic": getattr(chan, 'topic', None),
                "nsfw": getattr(chan, 'nsfw', False)
            })

        user_path = self.user_backup(srv.id, inter.user.id)
        os.makedirs(user_path, exist_ok=True)
        the_file = os.path.join(user_path, f"{name}.json")
        write_data(the_file, data)
        
        await inter.followup.send(f"✅ Backup **{name}**  created successfully!")

    @app_commands.command(name="backup_load", description="☢️ Wipe server and load backup")
    @app_commands.describe(name="Name of backup to load")
    async def backup_load(self, inter: discord.Interaction, name: str):
        if not await can_do(inter, "administrator"): 
            return await inter.response.send_message("❌ Admin only!", ephemeral=True)

        user_path = self.user_backup(inter.guild_id, inter.user.id)
        the_file = os.path.join(user_path, f"{name}.json")
        
        if not os.path.exists(the_file):
            return await inter.response.send_message("❌ Backup not found!", ephemeral=True)

        view = ConfirmLoadView(inter, name, self)
        await inter.response.send_message(
            txt=f"🚨 **CAUTION**: This will **DELETE EVERYTHING** in the server and replace it with backup **{name}**. Are you absolutely sure?", 
            view=view
        )

    async def execute_nuclear_restore(self, inter: discord.Interaction, name: str):
        user_path = self.user_backup(inter.guild_id, inter.user.id)
        the_file = os.path.join(user_path, f"{name}.json")
        data = read_data(the_file)
        srv = inter.guild

        for chan in srv.channels:
            try:
                if chan.id != inter.channel_id:
                    await chan.delete()
            except: pass

        for role in srv.roles:
            if not role.is_default() and not role.managed and role.position < srv.me.top_role.position:
                try:
                    await role.delete()
                except: pass

        for r_data in data.get("roles", []):
            try:
                await srv.create_role(
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
                new_cat = await srv.create_category(name=c_data["name"])
                cat_map[c_data["name"]] = new_cat
            except: pass

        first_text_channel = None
        for ch_data in data.get("channels", []):
            try:
                cat = cat_map.get(ch_data["category"])
                if ch_data["type"] == "text":
                    new_ch = await srv.create_text_channel(name=ch_data["name"], category=cat, topic=ch_data["topic"], nsfw=ch_data["nsfw"])
                    if not first_text_channel: first_text_channel = new_ch
                elif ch_data["type"] == "voice":
                    await srv.create_voice_channel(name=ch_data["name"], category=cat)
            except: pass

        try:
            old_channel = srv.get_channel(inter.channel_id)
            if old_channel:
                await old_channel.delete()
        except: pass

        if first_text_channel:
            await first_text_channel.send(f"✅ Backup **{name}** loaded successfully.")

    @app_commands.command(name="backup_list", description="📋 List your server backups")
    async def backup_list(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=False)
        user_path = self.user_backup(inter.guild_id, inter.user.id)
        
        if not os.path.exists(user_path) or not os.listdir(user_path):
            await inter.followup.send("📋 You haven't created any backups yet!")
            return

        backups = [f.replace(".json", "") for f in os.listdir(user_path) if f.endswith(".json")]
        emb = discord.Embed(title=f"📋 {inter.user.name}'s Backups", color=discord.Color.blue())
        emb.description = "\n".join([f"• `{b}`" for b in backups])
        await inter.followup.send(emb=emb)

async def setup(bot):
    await bot.add_cog(Backups(bot))
