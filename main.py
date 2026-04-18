import discord
from discord.ext import commands, tasks
import logging
import os
import asyncio
from config import token, grab_intents, backup_path
from utils.json_manager import setup_data
from config import (
    bans_json, mutes_json, warns_json, afk_json, 
    giveaways_json, reminders_json, levels_json, autoroles_json,
    antiswear_json, antispam_json, invites_json, botfilter_json
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RandomBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='/',
            intents=grab_intents(),
            help_command=None
        )

    async def setup_hook(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        splash = """
        \033[94m
        ██████╗  █████╗ ███╗   ██╗██████╗  ██████╗ ███╗   ███╗    ███╗   ███╗ ██████╗ ██████╗ 
        ██╔══██╗██╔══██╗████╗  ██║██╔══██╗██╔═══██╗████╗ ████║    ████╗ ████║██╔═══██╗██╔══██╗
        ██████╔╝███████║██╔██╗ ██║██║  ██║██║   ██║██╔████╔██║    ██╔████╔██║██║   ██║██║  ██║
        ██╔══██╗██╔══██║██║╚██╗██║██║  ██║██║   ██║██║╚██╔╝██║    ██║╚██╔╝██║██║   ██║██║  ██║
        ██║  ██║██║  ██║██║ ╚████║██████╔╝╚██████╔╝██║ ╚═╝ ██║    ██║ ╚═╝ ██║╚██████╔╝██████╔╝
        ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝  ╚═════╝ ╚═╝     ╚═╝    ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ 
        \033[0m
        \033[92m[✓]\033[0m Initializing Random Moderation Bot v2.0...
        """
        print(splash)

        self.update_times = {}

        os.makedirs(backup_path, exist_ok=True)
        files_needed = [
            (bans_json, {}), (mutes_json, {}), (warns_json, {}), 
            (afk_json, {}), (giveaways_json, {}), (reminders_json, {}), 
            (levels_json, {}), (autoroles_json, {}), (antiswear_json, {}), 
            (antispam_json, {}), (invites_json, {}), (botfilter_json, {"blocklist": []}),
            ("database/economy.json", {})
        ]
        
        for the_file, default in files_needed:
            setup_data(the_file, default)

        cog_dirs = ['commands', 'core']
        cogs_ready = 0
        for folder in cog_dirs:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        path = os.path.join(root, file)
                        self.update_times[path] = os.path.getmtime(path)
                        ext = path.replace(os.sep, '.')[:-3]
                        try:
                            await self.load_extension(ext)
                            cogs_ready += 1
                            print(f"\033[92m[✓]\033[0m Loaded extension: {ext}")
                        except Exception as e:
                            print(f"\033[91m[✗]\033[0m Failed to load extension {ext}: {e}")

        self.auto_reload.start()
        print(f"\n\033[94m» Loaded {cogs_ready} extensions successfully.\033[0m")
        print(f"\033[94m» Bot is ready.\033[0m\n")

    @tasks.loop(seconds=2)
    async def auto_reload(self):
        cog_dirs = ['commands', 'core']
        for folder in cog_dirs:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        path = os.path.join(root, file)
                        mod_t = os.path.getmtime(path)
                        
                        if path in self.update_times:
                            if mod_t > self.update_times[path]:
                                ext = path.replace(os.sep, '.')[:-3]
                                try:
                                    await self.reload_extension(ext)
                                    self.update_times[path] = mod_t
                                    print(f"\033[94m[⚡]\033[0m Reloaded: {ext}")
                                except Exception as e:
                                    print(f"\033[91m[✗]\033[0m Failed to reload {ext}: {e}")
                        else:
                            self.update_times[path] = mod_t
                            ext = path.replace(os.sep, '.')[:-3]
                            try:
                                await self.load_extension(ext)
                                print(f"\033[32m[+]\033[0m Loaded new extension: {ext}")
                            except Exception as e:
                                print(f"\033[91m[✗]\033[0m Failed to load new extension {ext}: {e}")

    @auto_reload.before_loop
    async def wait_up(self):
        await self.wait_until_ready()

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"\033[92m» SUCCESS: Logged in as {self.user.name}#{self.user.discriminator}\033[0m")
        print(f"\033[94m» Prefix: {self.command_prefix} | Latency: {round(self.latency * 1000)}ms\033[0m\n")

async def main():
    bot = RandomBot()
    async with bot:
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
