import os
import time
import asyncio
import requests

import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
RIOT_PLATFORM = os.getenv("RIOT_PLATFORM", "na1").lower()
TEST_GUILD_ID = int(os.getenv("TEST_GUILD_ID"))


def build_status_url(platform: str) -> str:
    """Create the Riot status endpoint URL for the given platform."""
    return f"https://{platform}.api.riotgames.com/lol/status/v4/platform-data"


def interpret_riot_response(status_code: int, platform: str) -> str:
    """Turn a Riot API status code into a short message for Discord."""
    if status_code == 200:
        return f"Riot API OK on {platform.upper()}. Status endpoint reachable."
    if status_code == 403:
        return "Riot API key rejected or expired (403)."
    if status_code == 429:
        return "Rate limited by Riot (429). Try again later."
    return f"Riot API error {status_code} on {platform.upper()}."


def riot_status_check(platform: str, api_key: str) -> int:
    """Send a request to Riot’s status endpoint and return the HTTP status code."""
    url = build_status_url(platform)
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers, timeout=10)
    return response.status_code


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

_cache = {"expires_at": 0.0, "status_code": None}
CACHE_TTL_SECONDS = 30

_cooldowns = {}
COOLDOWN_SECONDS = 10


@bot.event
async def on_ready():
    """Run once when the bot successfully connects to Discord."""
    print(f"Online as {bot.user} | Servers: {len(bot.guilds)}")


@bot.event
async def setup_hook():
    """Sync slash commands to the test guild so they appear instantly."""
    guild = discord.Object(id=TEST_GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print("Slash commands synced to test guild.")


@bot.tree.command(name="riotcheck", description="Check if the Riot API key works.")
async def riotcheck(interaction: discord.Interaction):
    """Check Riot API status endpoint and reply with the result."""
    now = time.time()
    user_id = interaction.user.id

    last_used = _cooldowns.get(user_id, 0.0)
    time_left = (last_used + COOLDOWN_SECONDS) - now
    if time_left > 0:
        await interaction.response.send_message(
            f"Chill dawg try again in {time_left:.1f}s.",
            ephemeral=True,
        )
        return

    _cooldowns[user_id] = now

    if _cache["status_code"] is not None and now < _cache["expires_at"]:
        message = interpret_riot_response(_cache["status_code"], RIOT_PLATFORM)
        await interaction.response.send_message(f"{message} (cached)", ephemeral=True)
        return

    try:
        status_code = await asyncio.to_thread(riot_status_check, RIOT_PLATFORM, RIOT_API_KEY)
        _cache["status_code"] = status_code
        _cache["expires_at"] = now + CACHE_TTL_SECONDS
        await interaction.response.send_message(
            interpret_riot_response(status_code, RIOT_PLATFORM),
            ephemeral=True,
        )
    except requests.exceptions.Timeout:
        await interaction.response.send_message("Riot API request timed out.", ephemeral=True)
    except Exception:
        await interaction.response.send_message("Unexpected error while contacting Riot API.", ephemeral=True)


bot.run(DISCORD_TOKEN)
