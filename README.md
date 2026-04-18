# 🛡️ Random's Moderation Bot

A powerful Discord moderation bot built with `discord.py`. Designed to provide advanced server management, advanced security, and community engagement tools.

## ✨ Features

### 🛡️ Advanced Moderation
- **Command Suite**: `ban`, `kick`, `timeout`, `warn`, `purge`, `slowmode`, and `nick`.
- **Role Management**: Easily add, remove, and manage user roles via commands.
- **Dynamic Logging**: Track moderator actions and server events in real-time.

### 🔒 Security & Protection
- **Anti-Spam**: Prevent rapid messaging.
- **Anti-Invite**: Automatically filter and manage Discord invite links.
- **Anti-Swear**: Customizable filter with automated actions.
- **Join Filters**: Block suspicious accounts or bots from joining your community.

### 🛠️ Utility & Tools
- **AFK System**: Notify others when you're away with custom status messages.
- **Reminders**: Set personal or server wide alerts for important events.
- **Backups**: Securely backup guild configurations and structures.
- **Economy & XP**: Reward active members with a leveling system.

### ⚙️ Configuration Variables
- **`token`**: Your Discord Bot Token.
- **`boss_id`**: The Discord ID of the bot owner/main administrator. This is used to identify who has full control over the bot and can bypass certain permission checks.
- **`prefix`**: The prefix for legacy commands.

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/randomname2323/Randoms-Moderation-Bot.git
   cd Randoms-Moderation-Bot
   ```

2. **Install dependencies:**
   ```bash
   pip install discord.py logging asyncio
   ```

3. **Configure the bot:**
   - Open `config.py` and replace `token` with your bot's token from the [Discord Developer Portal](https://discord.com/developers/applications).
   - Adjust `boss_id` and other settings as needed.

4. **Launch the bot:**
   ```bash
   python main.py
   ```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Built with ❤️ by RandomName*
