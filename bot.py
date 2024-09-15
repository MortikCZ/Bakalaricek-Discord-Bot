import discord
from discord.ext import commands, tasks
import datetime
from datetime import datetime, timedelta
from bakapiv2 import BakapiUser
import json
from collections import defaultdict
import os

with open('config.json') as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["bot"]["token"]
BAKALARI_USERNAME = config["bakalari"]["username"]
BAKALARI_PASSWORD = config["bakalari"]["password"]
BAKALARI_URL = config["bakalari"]["url"]
SUBSTITUTIONS_CHANNEL_ID = config["discord"]["substitutions_channel_id"] if "discord" in config else None
SUBST_CHANGE_CHANNEL_ID = config["discord"]["subst_change_channel_id"] if "discord" in config else None

bakalari_user = BakapiUser(url=BAKALARI_URL, username=BAKALARI_USERNAME, password=BAKALARI_PASSWORD)

intents = discord.Intents.all() 

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    substitutions_embed.start()
    check_timetable.start()

CONFIG_FILE = 'config.json'

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

PREVIOUS_TIMETABLE_FILE = 'previous_timetable.json'

def load_previous_timetable():
    if os.path.exists(PREVIOUS_TIMETABLE_FILE):
        with open(PREVIOUS_TIMETABLE_FILE, 'r') as file:
            return json.load(file)
    return None

def save_previous_timetable(timetable):
    with open(PREVIOUS_TIMETABLE_FILE, 'w') as file:
        json.dump(timetable, file, indent=4)

previous_timetable = load_previous_timetable()

def get_next_weekday(date):
    while date.weekday() >= 5:  
        date += timedelta(days=1)
    return date

@tasks.loop(minutes=30)
async def substitutions_embed():
    config = load_config()
    if 'discord' not in config or 'substitutions_channel_id' not in config['discord']:
        return
    channel_id = config['discord']['substitutions_channel_id']
    channel = bot.get_channel(channel_id)
    if channel is None:
        return

    today = datetime.now()
    if today.weekday() >= 5: 
        today = get_next_weekday(today)

    substitutions = bakalari_user.get_substitutions()
    week_number = today.isocalendar()[1]
    embed = discord.Embed(title=f"Změny v rozvrhu ({week_number}.týden)", color=0x02a2e2)

    changes_by_date = defaultdict(list)
    for change in substitutions['Changes']:
        date_string = change['Day']
        date_object = datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        if date_object.isocalendar()[1] != week_number:
            continue
        date = f"{date_object.strftime('%d.%m.')}"
        hour_number = f"🕑 {change['Hours']}"
        description = change['Description']
        changes_by_date[date].append(f"{hour_number} - {description}")

    for date, changes in changes_by_date.items():
        embed.add_field(name=date, value="\n".join(changes), inline=False)

    now = datetime.now()
    embed.set_footer(text=f"Poslední update: {now.strftime('%d.%m. %H:%M:%S')}")

    if 'subst_message_id' in config['discord'] and config['discord']['subst_message_id'] is not None:
        try:
            message_id = config['discord']['subst_message_id']
            message = await channel.fetch_message(message_id)
            await message.edit(embed=embed)
        except discord.NotFound:
            message = await channel.send(embed=embed)
            config['discord']['subst_message_id'] = message.id
            save_config(config)
    else:
        message = await channel.send(embed=embed)
        config['discord']['subst_message_id'] = message.id
        save_config(config)

@tasks.loop(minutes=30)
async def check_timetable():
    global previous_timetable

    current_date = datetime.today().date()

    if current_date.weekday() > 4:  
        days_ahead = 7 - current_date.weekday()  
        current_date = current_date + timedelta(days_ahead)

    current_date_str = current_date.strftime("%Y-%m-%d")
    current_date_display = current_date.strftime("%d.%m.")

    timetable = bakalari_user.get_timetable_actual(date=current_date_str)

    changes = []
    for day in timetable['Days']:
        for atom in day['Atoms']:
            if atom.get('Change'):
                changes.append({
                    'Date': day['Date'],
                    'HourId': atom['HourId'],
                    'Change': atom['Change'],
                    'Description': atom.get('Description', 'No description')
                })

    if previous_timetable is not None:
        new_changes = [change for change in changes if change not in previous_timetable]
    else:
        new_changes = changes

    if new_changes:
        channel = bot.get_channel(SUBST_CHANGE_CHANNEL_ID)
        role_id = config['discord']['subst_change_role_id']
        role_mention = f"<@&{role_id}>"
        for change in new_changes:
            date = change['Date'].split('T')[0]
            formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.")
            hour_id = change['HourId']
            change_details = change['Change']
            change_day = datetime.strptime(change_details.get('Day', 'Unknown day').split('T')[0], "%Y-%m-%d").strftime("%d.%m.")
            change_hours = change_details.get('Hours', 'Unknown hours')
            change_description = change_details.get('Description', 'No description')
            message = (
                f"{role_mention}\n"
                f"# Nová změna v rozvrhu!\n"
                f"**Datum:** {change_day}\n"
                f"**Číslo hodiny:** {change_hours}\n"
                f"**Popis:** {change_description}"
            )
            await channel.send(message)

    previous_timetable = changes
    save_previous_timetable(previous_timetable)

bot.run(BOT_TOKEN)