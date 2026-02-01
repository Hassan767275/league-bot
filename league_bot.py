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
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

_cache = {"expires_at": 0.0, "status_code": None}
CACHE_TTL_SECONDS = 30

@bot.event
async def on_ready():
    """Run once when the bot successfully connects to Discord."""
    print(f"Online as {bot.user} | Servers: {len(bot.guilds)}")

@bot.command(name="riotcheck")
@commands.cooldown(1, 10, commands.BucketType.user)
async def riotcheck(ctx):
    """Check if the Riot API key works by calling the status endpoint."""
    now = time.time()

    if _cache["status_code"] is not None and now < _cache["expires_at"]:
        message = interpret_riot_response(_cache["status_code"], RIOT_PLATFORM)
        await ctx.send(f"{message} (cached)")
        return

    try:
        status_code = await asyncio.to_thread(
            riot_status_check, RIOT_PLATFORM, RIOT_API_KEY
        )
        _cache["status_code"] = status_code
        _cache["expires_at"] = now + CACHE_TTL_SECONDS
        await ctx.send(interpret_riot_response(status_code, RIOT_PLATFORM))
    except requests.exceptions.Timeout:
        await ctx.send("Riot API request timed out.")
    except Exception:
        await ctx.send("Unexpected error while contacting Riot API.")

@riotcheck.error
async def riotcheck_error(ctx, error):
    """Handle cooldown and command errors for the riotcheck command."""
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Chill dawg try again in {error.retry_after:.1f}s.")
    else:
        await ctx.send("Command error.")

bot.run(DISCORD_TOKEN)