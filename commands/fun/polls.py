import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, UTC

class PollView(discord.ui.View):
    def __init__(self, choice1, choice2):
        super().__init__(timeout=None)
        self.choice1_label = choice1
        self.choice2_label = choice2
        self.votes1 = 0
        self.votes2 = 0
        self.voted_users = set()

    @discord.ui.button(label="Option 1", style=discord.ButtonStyle.primary)
    async def opt1(self, inter: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(inter, 1)

    @discord.ui.button(label="Option 2", style=discord.ButtonStyle.secondary)
    async def opt2(self, inter: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(inter, 2)

    async def handle_vote(self, inter: discord.Interaction, choice):
        if inter.user.id in self.voted_users:
            return await inter.response.send_message("❌ You already voted!", ephemeral=True)
        
        self.voted_users.add(inter.user.id)
        if choice == 1: self.votes1 += 1
        else: self.votes2 += 1

        emb = inter.msg.embeds[0]
        total = self.votes1 + self.votes2
        p1 = (self.votes1 / total) * 100 if total > 0 else 0
        p2 = (self.votes2 / total) * 100 if total > 0 else 0
        
        emb.set_field_at(0, name=f"🔹 {self.choice1_label}", value=f"Votes: `{self.votes1}` ({p1:.1f}%)", inline=False)
        emb.set_field_at(1, name=f"🔸 {self.choice2_label}", value=f"Votes: `{self.votes2}` ({p2:.1f}%)", inline=False)
        
        await inter.response.edit_message(emb=emb)

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="📊 Create a poll")
    async def poll(self, inter: discord.Interaction, question: str, choice1: str, choice2: str):
        emb = discord.Embed(
            title=f"📊 {question}", 
            color=discord.Color.blue(), 
            timestamp=datetime.now(UTC)
        )
        emb.add_field(name=f"🔹 {choice1}", value="Votes: `0` (0.0%)", inline=False)
        emb.add_field(name=f"🔸 {choice2}", value="Votes: `0` (0.0%)", inline=False)
        emb.set_footer(text=f"Poll by {inter.user.display_name}")

        view = PollView(choice1, choice2)
        view.children[0].label = f"Vote {choice1}"
        view.children[1].label = f"Vote {choice2}"
        
        await inter.response.send_message(emb=emb, view=view)

async def setup(bot):
    await bot.add_cog(Polls(bot))
