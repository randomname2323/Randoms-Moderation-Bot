import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Select, Button
from datetime import datetime, UTC

class HelpView(View):
    def __init__(self, bot, user):
        super().__init__(timeout=120)
        self.bot = bot
        self.user = user
        self.add_item(HelpSelect(bot))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ This menu is not for you!", ephemeral=False)
            return False
        return True

class HelpSelect(Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            discord.SelectOption(label="Moderation", description="Server management & protection", emoji="🛡️"),
            discord.SelectOption(label="Fun", description="Games and entertainment", emoji="🎉"),
            discord.SelectOption(label="Utility", description="Useful tools and info", emoji="🛠️"),
            discord.SelectOption(label="Leveling", description="Rankings and XP", emoji="🏆"),
            discord.SelectOption(label="Reminders", description="Set and manage alerts", emoji="⏰"),
            discord.SelectOption(label="Backups", description="Guild backup system", emoji="💾")
        ]
        super().__init__(placeholder="Choose a category to explore...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        category = self.values[0]
        embed = discord.Embed(
            title=f"{self.emoji_for(category)} {category} Commands",
            description=f"Explore the commands in the **{category}** category.",
            color=discord.Color.blue(),
            timestamp=datetime.now(UTC)
        )
        
        commands_list = self.get_commands_for_category(category)
        if not commands_list:
            embed.description = "No commands found in this category."
        else:
            for cmd in commands_list:
                embed.add_field(name=f"`/{cmd.name}`", value=cmd.description or "No description", inline=False)
        
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        await interaction.edit_original_response(embed=embed, view=self.view)

    def emoji_for(self, name):
        mapping = {"Moderation": "🛡️", "Fun": "🎉", "Utility": "🛠️", "Leveling": "🏆", "Reminders": "⏰", "Backups": "💾"}
        return mapping.get(name, "🔘")

    def get_commands_for_category(self, category):
        category_lower = category.lower()
        commands_list = []
        for cmd in self.bot.tree.get_commands():
            module_name = ""
            if hasattr(cmd, 'callback'):
                module_name = cmd.callback.__module__
            elif hasattr(cmd, 'binding'):
                module_name = cmd.binding.__module__
            
            if category_lower in module_name.split('.'):
                commands_list.append(cmd)
        return commands_list

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="📚 View the commands of this bot")
    async def help(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        embed = discord.Embed(
            title="✨ Random Moderation | Commands",
            description=(
                "Welcome to the **Random Moderation** help center. "
                "Select a category below to see command usage.\n\n"
                "**Quick Stats:**\n"
                f"• Commands: `{len(self.bot.tree.get_commands())}`\n"
                f"• Latency: `{round(self.bot.latency * 1000)}ms`\n"
            ),
            color=discord.Color.blue(),
            timestamp=datetime.now(UTC)
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Random Moderation Bot", icon_url=self.bot.user.display_avatar.url)
        
        view = HelpView(self.bot, interaction.user)
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))
