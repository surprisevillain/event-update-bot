import discord
from discord.ext import tasks, commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import pytz
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1413997970155765912
EASTERN = pytz.timezone("America/New_York")
scheduler = AsyncIOScheduler(timezone=EASTERN)

async def start_event(event_id):
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return
    events = await guild.fetch_scheduled_events()
    for event in events:
        if event.id == event_id:
            try:
                await event.start()
                print(f"Started event: {event.name}")
            except Exception as e:
                print(f"Error starting {event.name}: {e}")

async def end_event(event_id):
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return
    events = await guild.fetch_scheduled_events()
    for event in events:
        if event.id == event_id:
            try:
                channel = bot.get_channel(event.channel_id)
                # Wait until channel is empty, check every 30s
                while channel and len(channel.members) > 0:
                    now_eastern = datetime.datetime.now(EASTERN)
                    # Force end at 11pm regardless
                    if now_eastern.hour >= 23:
                        break
                    await discord.utils.sleep_until(datetime.datetime.now(EASTERN) + datetime.timedelta(seconds=30))
                await event.end()
                print(f"Ended event: {event.name}")
            except Exception as e:
                print(f"Error ending {event.name}: {e}")

async def schedule_events():
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        return

    scheduler.remove_all_jobs()
    events = await guild.fetch_scheduled_events()
    now = datetime.datetime.now(EASTERN)

    for event in events:
        if event.entity_type not in [discord.EntityType.voice, discord.EntityType.stage_voice]:
            continue

        start = event.start_time.astimezone(EASTERN) + datetime.timedelta(minutes=2)
        end = event.end_time.astimezone(EASTERN)

        if start > now:
            scheduler.add_job(start_event, 'date', run_date=start, args=[event.id], id=f"start_{event.id}")
            print(f"Scheduled start for: {event.name} at {start}")

        if end > now:
            scheduler.add_job(end_event, 'date', run_date=end, args=[event.id], id=f"end_{event.id}")
            print(f"Scheduled end for: {event.name} at {end}")

@tasks.loop(hours=1)
async def refresh_schedule():
    await schedule_events()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    scheduler.start()
    await schedule_events()
    refresh_schedule.start()

bot.run(os.environ["DISCORD_TOKEN"])
