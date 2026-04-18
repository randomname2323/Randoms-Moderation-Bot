import os
import discord

token = 'your token comes here'

db_path = 'database'
bans_json = os.path.join(db_path, 'tempbans.json')
mutes_json = os.path.join(db_path, 'tempmutes.json')
warns_json = os.path.join(db_path, 'warnings.json')
afk_json = os.path.join(db_path, 'afk.json')
giveaways_json = os.path.join(db_path, 'giveaways.json')
reminders_json = os.path.join(db_path, 'reminders.json')
levels_json = os.path.join(db_path, 'levels.json')
autoroles_json = os.path.join(db_path, 'autoroles.json')
antiswear_json = os.path.join(db_path, 'antiswear.json')
antispam_json = os.path.join(db_path, 'antispam.json')
invites_json = os.path.join(db_path, 'invites.json')
botfilter_json = os.path.join(db_path, 'filter_join_bot.json')
bad_words_txt = "bad_words.txt"
backup_path = 'backups'

boss_id = #your id
prefix = '/'

def grab_intents():
    intents = discord.Intents.default()
    intents.members = True
    intents.guilds = True
    intents.message_content = True
    intents.presences = True
    return intents
