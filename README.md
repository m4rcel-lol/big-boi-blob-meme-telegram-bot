# big-boi-blob-meme-telegram-bot
Big Boi Blob is a Telegram bot that sends a random meme from it's project's repository with either /start command or by using a special command to set up daily memes.

## Setup with Docker Compose (24/7 operation)

1. Clone this repository
2. Copy `.env.example` to `.env` and add your Telegram bot token:
   ```bash
   cp .env.example .env
   # Edit .env and set TELEGRAM_BOT_TOKEN=your_actual_token
   ```
3. Start the bot with Docker Compose:
   ```bash
   docker compose up -d
   ```
4. View logs:
   ```bash
   docker compose logs -f
   ```
5. Stop the bot:
   ```bash
   docker compose down
   ```

The bot will automatically restart if it crashes and will start automatically when your system boots.

## Manual Setup (without Docker)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your bot token
3. Run the bot:
   ```bash
   python bot.py
   ```
