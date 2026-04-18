import os
import discord

# REPLACE THIS WITH YOUR TOKEN
TOKEN = 'YOUR_BOT_TOKEN_HERE'

DB_DIR = 'database'
TEMPBANS_FILE = os.path.join(DB_DIR, 'tempbans.json')
TEMPMUTES_FILE = os.path.join(DB_DIR, 'tempmutes.json')
WARNINGS_FILE = os.path.join(DB_DIR, 'warnings.json')
AFK_FILE = os.path.join(DB_DIR, 'afk.json')
GIVEAWAYS_FILE = os.path.join(DB_DIR, 'giveaways.json')
REMINDERS_FILE = os.path.join(DB_DIR, 'reminders.json')
LEVELS_FILE = os.path.join(DB_DIR, 'levels.json')
AUTOROLES_FILE = os.path.join(DB_DIR, 'autoroles.json')
ANTISWEAR_FILE = os.path.join(DB_DIR, 'antiswear.json')
ANTISPAM_FILE = os.path.join(DB_DIR, 'antispam.json')
INVITES_FILE = os.path.join(DB_DIR, 'invites.json')
FILTER_JOIN_BOT_FILE = os.path.join(DB_DIR, 'filter_join_bot.json')
BAD_WORDS_FILE = "bad_words.txt"
BACKUPS_DIR = 'backups'

# The Discord ID of the bot owner
ALLOWED_USER_ID = 000000000000000000 
DEFAULT_PREFIX = '/'

def get_intents():
    intents = discord.Intents.default()
    intents.members = True
    intents.guilds = True
    intents.message_content = True
    intents.presences = True
    return intents
