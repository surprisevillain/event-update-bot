import discord
from discord.ext import tasks, commands
import datetime
import pytz
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1413997970155765912
CHECK_INTERVAL = 30
EASTERN = pytz.timezone("America/New_York")

@tasks.loop(seconds=CHECK_INTERVAL)
async def manage_events():
    now_eastern = datetime.datetime.now(EASTERN)

    if now_eastern.weekday() > 3 or not (17 <= now_eastern.hour < 23):
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

        # Hard force-end at 11pm regardless of who's in the channel
        force_end_time = now_eastern.replace(hour=23, minute=0, second=0, microsecond=0)

        if event.status != discord.EventStatus.active and start + datetime.timedelta(minutes=2) <= now_eastern < end:
            try:
                await event.start()
                print(f"Started event: {event.name}")
            except Exception as e:
                print(f"Error starting {event.name}: {e}")

        elif event.status != discord.EventStatus.completed and now_eastern >= end:
            try:
                channel = bot.get_channel(event.channel_id)
                if channel is None or len(channel.members) == 0 or now_eastern >= force_end_time:
                    await event.end()
                    print(f"Ended event: {event.name}")
            except Exception as e:
                print(f"Error ending {event.name}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    manage_events.start()

bot.run(os.environ["DISCORD_TOKEN"])
