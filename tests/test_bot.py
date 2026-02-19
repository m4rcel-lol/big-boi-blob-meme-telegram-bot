import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import bot


def _mock_memes_dir(files):
    """Return a MagicMock MEMES_DIR whose iterdir() yields the given files."""
    mock_dir = MagicMock(spec=Path)
    mock_dir.iterdir.return_value = iter(files)
    return mock_dir


class TestGetRandomMeme(unittest.TestCase):
    def test_returns_path_from_memes_dir(self):
        fake_meme = MagicMock(spec=Path)
        fake_meme.suffix = ".png"
        with patch("bot.MEMES_DIR", _mock_memes_dir([fake_meme])):
            result = bot.get_random_meme()
        self.assertEqual(result, fake_meme)

    def test_returns_none_when_no_memes(self):
        with patch("bot.MEMES_DIR", _mock_memes_dir([])):
            result = bot.get_random_meme()
        self.assertIsNone(result)

    def test_ignores_non_image_files(self):
        txt_file = MagicMock(spec=Path)
        txt_file.suffix = ".txt"
        with patch("bot.MEMES_DIR", _mock_memes_dir([txt_file])):
            result = bot.get_random_meme()
        self.assertIsNone(result)

    def test_memes_dir_contains_images(self):
        """The memes directory in the repository must contain at least one image."""
        memes = [
            p
            for p in bot.MEMES_DIR.iterdir()
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}
        ]
        self.assertGreater(len(memes), 0, "memes/ directory should contain at least one image")


class TestStartCommand(unittest.IsolatedAsyncioTestCase):
    async def test_start_sends_meme(self):
        fake_meme = Path(__file__).parent.parent / "memes" / "blob_happy.png"
        update = MagicMock()
        update.message.reply_text = AsyncMock()
        update.message.reply_photo = AsyncMock()
        context = MagicMock()

        with patch("bot.get_random_meme", return_value=fake_meme):
            await bot.start(update, context)

        update.message.reply_text.assert_awaited_once()
        update.message.reply_photo.assert_awaited_once()

    async def test_start_no_memes(self):
        update = MagicMock()
        update.message.reply_text = AsyncMock()
        update.message.reply_photo = AsyncMock()
        context = MagicMock()

        with patch("bot.get_random_meme", return_value=None):
            await bot.start(update, context)

        update.message.reply_text.assert_awaited_once()
        update.message.reply_photo.assert_not_awaited()


class TestDailyCommand(unittest.IsolatedAsyncioTestCase):
    async def test_daily_schedules_job(self):
        update = MagicMock()
        update.effective_chat.id = 12345
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.job_queue.get_jobs_by_name.return_value = []

        await bot.daily(update, context)

        context.job_queue.run_daily.assert_called_once()
        update.message.reply_text.assert_awaited_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("Subscribed", text)

    async def test_daily_replaces_existing_job(self):
        update = MagicMock()
        update.effective_chat.id = 12345
        update.message.reply_text = AsyncMock()
        existing_job = MagicMock()
        context = MagicMock()
        context.job_queue.get_jobs_by_name.return_value = [existing_job]

        await bot.daily(update, context)

        existing_job.schedule_removal.assert_called_once()
        context.job_queue.run_daily.assert_called_once()


class TestStopDailyCommand(unittest.IsolatedAsyncioTestCase):
    async def test_stopdaily_removes_job(self):
        update = MagicMock()
        update.effective_chat.id = 12345
        update.message.reply_text = AsyncMock()
        existing_job = MagicMock()
        context = MagicMock()
        context.job_queue.get_jobs_by_name.return_value = [existing_job]

        await bot.stop_daily(update, context)

        existing_job.schedule_removal.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("Unsubscribed", text)

    async def test_stopdaily_no_subscription(self):
        update = MagicMock()
        update.effective_chat.id = 12345
        update.message.reply_text = AsyncMock()
        context = MagicMock()
        context.job_queue.get_jobs_by_name.return_value = []

        await bot.stop_daily(update, context)

        update.message.reply_text.assert_awaited_once()
        text = update.message.reply_text.call_args[0][0]
        self.assertIn("don't have an active", text)


if __name__ == "__main__":
    unittest.main()
