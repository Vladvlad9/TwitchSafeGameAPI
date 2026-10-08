import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from settings import settings
from src.twitch import TwitchBot

logger = logging.getLogger(__name__)


def _log_bot_task_result(task: asyncio.Task[None]) -> None:
    if task.cancelled():
        return

    exception = task.exception()
    if exception is not None:
        logger.error(
            "Twitch client stopped unexpectedly",
            exc_info=(type(exception), exception, exception.__traceback__),
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    bot = TwitchBot(
        client_id=settings.TWITCH.CLIENT_ID,
        client_secret=settings.TWITCH.CLIENT_SECRET,
        bot_id=settings.TWITCH.BOT_ID,
        broadcaster_id=settings.TWITCH.OWNER_ID,
        oauth_host=settings.TWITCH.OAUTH_HOST,
        oauth_port=settings.TWITCH.OAUTH_PORT,
        redirect_uri=settings.TWITCH.REDIRECT_URI,
    )

    app.state.twitch_bot = bot
    bot_task = asyncio.create_task(
        bot.start(),
        name="twitch-bot",
    )
    bot_task.add_done_callback(_log_bot_task_result)

    try:
        yield
    finally:
        await bot.close()

        bot_task.cancel()

        with suppress(asyncio.CancelledError):
            await bot_task
