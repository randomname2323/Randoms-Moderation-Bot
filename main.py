import discord
from discord.ext import commands, tasks
import logging
import os
import asyncio
from config import TOKEN, get_intents, BACKUPS_DIR
from utils.json_manager import init_json_file
from config import (
    TEMPBANS_FILE, TEMPMUTES_FILE, WARNINGS_FILE, AFK_FILE, 
    GIVEAWAYS_FILE, REMINDERS_FILE, LEVELS_FILE, AUTOROLES_FILE,
    ANTISWEAR_FILE, ANTISPAM_FILE, INVITES_FILE, FILTER_JOIN_BOT_FILE
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RandomBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='/',
            intents=get_intents(),
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

        self.last_modified = {}

        os.makedirs(BACKUPS_DIR, exist_ok=True)
        files_to_init = [
            (TEMPBANS_FILE, {}), (TEMPMUTES_FILE, {}), (WARNINGS_FILE, {}), 
            (AFK_FILE, {}), (GIVEAWAYS_FILE, {}), (REMINDERS_FILE, {}), 
            (LEVELS_FILE, {}), (AUTOROLES_FILE, {}), (ANTISWEAR_FILE, {}), 
            (ANTISPAM_FILE, {}), (INVITES_FILE, {}), (FILTER_JOIN_BOT_FILE, {"blocklist": []}),
            ("database/economy.json", {})
        ]
        
        for file_path, default in files_to_init:
            init_json_file(file_path, default)

        cog_folders = ['commands', 'core']
        loaded_count = 0
        for folder in cog_folders:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        path = os.path.join(root, file)
                        self.last_modified[path] = os.path.getmtime(path)
                        module = path.replace(os.sep, '.')[:-3]
                        try:
                            await self.load_extension(module)
                            loaded_count += 1
                            print(f"\033[92m[✓]\033[0m Loaded extension: {module}")
                        except Exception as e:
                            print(f"\033[91m[✗]\033[0m Failed to load extension {module}: {e}")

        self.hot_reload_loop.start()
        print(f"\n\033[94m» Loaded {loaded_count} extensions successfully.\033[0m")
        print(f"\033[94m» Bot is ready.\033[0m\n")

    @tasks.loop(seconds=2)
    async def hot_reload_loop(self):
        cog_folders = ['commands', 'core']
        for folder in cog_folders:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        path = os.path.join(root, file)
                        mtime = os.path.getmtime(path)
                        
                        if path in self.last_modified:
                            if mtime > self.last_modified[path]:
                                module = path.replace(os.sep, '.')[:-3]
                                try:
                                    await self.reload_extension(module)
                                    self.last_modified[path] = mtime
                                    print(f"\033[94m[⚡]\033[0m Reloaded: {module}")
                                except Exception as e:
                                    print(f"\033[91m[✗]\033[0m Failed to reload {module}: {e}")
                        else:
                            self.last_modified[path] = mtime
                            module = path.replace(os.sep, '.')[:-3]
                            try:
                                await self.load_extension(module)
                                print(f"\033[32m[+]\033[0m Loaded new extension: {module}")
                            except Exception as e:
                                print(f"\033[91m[✗]\033[0m Failed to load new extension {module}: {e}")

    @hot_reload_loop.before_loop
    async def before_hot_reload_loop(self):
        await self.wait_until_ready()

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"\033[92m» SUCCESS: Logged in as {self.user.name}#{self.user.discriminator}\033[0m")
        print(f"\033[94m» Prefix: {self.command_prefix} | Latency: {round(self.latency * 1000)}ms\033[0m\n")

async def main():
    bot = RandomBot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
