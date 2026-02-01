# League of Legends Discord Bot

This repository contains a Discord bot that connects to the Riot Games API.
Follow the steps below to get the bot running locally.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Hassan767275/league-bot.git
```

---

### 2. Create a Virtual Environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal.

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create the `.env` File

Create a file named `.env` in the project root (do NOT commit this file).

```env
DISCORD_TOKEN=your_discord_bot_token_here
RIOT_API_KEY=your_riot_api_key_here
RIOT_PLATFORM=na1
TEST_GUILD_ID=your_discord_server_id_here
```

---

### 5. Discord Bot Setup

1. Go to the Discord Developer Portal
2. Create a new application
3. Add a bot
4. Copy the bot token into `.env`
5. Under OAuth2 → URL Generator:
   - Scopes:
     - bot
6. Invite the bot to your server

---

### 6. Get a Riot API Key

1. Go to the Riot Developer Portal
2. Log in
3. Generate a Development API Key
4. Paste it into `.env`

---

### 7. Run the Bot

```bash
python bot.py
```

---

### 8. Test the Bot

In your Discord server:

1. Type `/`
2. Select `riotcheck`
3. Run the command

---

## Future Features Roadmap

### PHASE 1 — Core Functionality

- [ ] Account Linking
- [ ] Rank Lookup
- [ ] Region Handling
- [ ] Safety

### PHASE 2 — Tracking Features

- [ ] Last Match
- [ ] Recent Matches
- [ ] Champion Stats
- [ ] Winrate Summary

### PHASE 3 — Quality of Life

- [ ] Better Output
- [ ] Help & UX
- [ ] Persistence
- [ ] Admin Controls

### PHASE 4 — Optional

- [ ] Match history graphs
- [ ] Rank change tracking
- [ ] LP gain/loss per game
- [ ] Clash stats
- [ ] ARAM / TFT support
- [ ] Auto-post rank updates
- [ ] Web dashboard
