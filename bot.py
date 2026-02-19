import logging
import os
import random
from datetime import time
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

MEMES_DIR = Path(__file__).parent / "memes"
DAILY_MEME_HOUR = 9  # 9:00 AM UTC


def get_random_meme() -> Path | None:
    """Return a random meme path from the memes directory, or None if empty."""
    memes = [
        p for p in MEMES_DIR.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}
    ]
    if not memes:
        return None
    return random.choice(memes)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a random blob meme on /start."""
    meme = get_random_meme()
    if meme is None:
        await update.message.reply_text("No memes available right now. 😢")
        return
    await update.message.reply_text("Here's a Big Boi Blob meme for you! 🎉")
    with open(meme, "rb") as f:
        await update.message.reply_photo(photo=f)


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Subscribe to daily blob memes with /daily."""
    chat_id = update.effective_chat.id

    for job in context.job_queue.get_jobs_by_name(str(chat_id)):
        job.schedule_removal()

    context.job_queue.run_daily(
        _send_daily_meme,
        time=time(DAILY_MEME_HOUR, 0, 0),
        chat_id=chat_id,
        name=str(chat_id),
    )
    await update.message.reply_text(
        f"✅ Subscribed! You'll receive a daily blob meme every day at {DAILY_MEME_HOUR}:00 UTC.\n"
        "Use /stopdaily to unsubscribe."
    )


async def stop_daily(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unsubscribe from daily blob memes with /stopdaily."""
    chat_id = update.effective_chat.id
    jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if not jobs:
        await update.message.reply_text("You don't have an active daily meme subscription.")
        return
    for job in jobs:
        job.schedule_removal()
    await update.message.reply_text("❌ Unsubscribed from daily blob memes.")


async def _send_daily_meme(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Job callback: send a daily meme to the subscribed chat."""
    meme = get_random_meme()
    if meme is None:
        return
    await context.bot.send_message(
        chat_id=context.job.chat_id, text="🌅 Here's your daily Big Boi Blob meme!"
    )
    with open(meme, "rb") as f:
        await context.bot.send_photo(chat_id=context.job.chat_id, photo=f)


def main() -> None:
    """Start the Big Boi Blob bot."""
    load_dotenv()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set.")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("stopdaily", stop_daily))

    logger.info("Big Boi Blob bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
