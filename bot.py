import discord
from discord.ext import tasks, commands
import datetime
import pytz
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1413997970155765912
CHECK_INTERVAL = 30  # seconds
EASTERN = pytz.timezone("America/New_York")

@tasks.loop(seconds=CHECK_INTERVAL)
async def manage_events():
    now_eastern = datetime.datetime.now(EASTERN)

    # Only run Monday-Thursday (0-3) between 5pm and 10pm ET
    if now_eastern.weekday() > 3 or not (17 <= now_eastern.hour < 22):
        return

    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return

    now = datetime.datetime.now(datetime.timezone.utc)
    events = await guild.fetch_scheduled_events()

    for event in events:
        if event.entity_type not in [discord.EntityType.voice, discord.EntityType.stage_voice]:
            continue

        start = event.start_time.astimezone(EASTERN)
        end = event.end_time.astimezone(EASTERN)
        now_eastern = now.astimezone(EASTERN)

        if event.status != discord.EventStatus.active and start <= now_eastern < end:
            try:
                await event.start()
                print(f"Started event: {event.name}")
            except Exception as e:
                print(f"Error starting {event.name}: {e}")

        elif event.status != discord.EventStatus.completed and now_eastern >= end:
            try:
                await event.end()
                print(f"Ended event: {event.name}")
            except Exception as e:
                print(f"Error ending {event.name}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    manage_events.start()

bot.run("import discord
from discord.ext import tasks, commands
import datetime
import pytz

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1413997970155765912
CHECK_INTERVAL = 30  # seconds
EASTERN = pytz.timezone("America/New_York")

@tasks.loop(seconds=CHECK_INTERVAL)
async def manage_events():
    now_eastern = datetime.datetime.now(EASTERN)

    # Only run Monday-Thursday (0-3) between 5pm and 10pm ET
    if now_eastern.weekday() > 3 or not (17 <= now_eastern.hour < 22):
        return

    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return

    now = datetime.datetime.now(datetime.timezone.utc)
    events = await guild.fetch_scheduled_events()

    for event in events:
        if event.entity_type not in [discord.EntityType.voice, discord.EntityType.stage_voice]:
            continue

        start = event.start_time.astimezone(EASTERN)
        end = event.end_time.astimezone(EASTERN)
        now_eastern = now.astimezone(EASTERN)

        if event.status != discord.EventStatus.active and start <= now_eastern < end:
            try:
                await event.start()
                print(f"Started event: {event.name}")
            except Exception as e:
                print(f"Error starting {event.name}: {e}")

        elif event.status != discord.EventStatus.completed and now_eastern >= end:
            try:
                await event.end()
                print(f"Ended event: {event.name}")
            except Exception as e:
                print(f"Error ending {event.name}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    manage_events.start()

bot.run(os.environ["DISCORD_TOKEN"])
