import logging

import twitchio
from starlette.requests import Request
from twitchio import eventsub, web

from src.game import GuessResult, RedisGameStore


logger = logging.getLogger(__name__)

SCOPES = twitchio.Scopes(
    user_read_chat=True,
    user_write_chat=True,
    user_bot=True,
)

GUESS_COMMAND = "!code"


def extract_guess(message: str) -> str | None:
    parts = message.strip().split(maxsplit=1)
    if len(parts) != 2 or parts[0].casefold() != GUESS_COMMAND:
        return None

    guess = parts[1].strip()
    return guess or None


class OAuthStarletteAdapter(web.StarletteAdapter):
    """Bind inside Docker while keeping the public OAuth callback stable."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        redirect_uri: str,
    ) -> None:
        self._public_redirect_uri = redirect_uri
        super().__init__(host=host, port=port)

    @property
    def redirect_url(self) -> str:
        return self._public_redirect_uri

    def _find_redirect(self, request: Request) -> str:
        # TwitchIO 3.3.2 drops the external port when the server binds to
        # 0.0.0.0 in Docker but the browser accesses it through localhost.
        return self._public_redirect_uri


class TwitchBot(twitchio.Client):
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        bot_id: str,
        broadcaster_id: str,
        oauth_host: str,
        oauth_port: int,
        redirect_uri: str,
        game_store: RedisGameStore,
    ) -> None:
        self.broadcaster_id = broadcaster_id
        self.game_store = game_store
        self._chat_subscribed = False

        adapter = OAuthStarletteAdapter(
            host=oauth_host,
            port=oauth_port,
            redirect_uri=redirect_uri,
        )

        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            bot_id=bot_id,
            scopes=SCOPES,
            adapter=adapter,
            redirect_uri=redirect_uri,
        )

    async def event_ready(self) -> None:
        logger.info("Twitch подключён")

        for user_id in self.tokens:
            logger.info("Найден Twitch-токен: user_id=%s", user_id)

        if self.bot_id not in self.tokens:
            logger.warning(
                "Токен бота отсутствует. Сначала выполните OAuth."
            )
            return

        await self.subscribe_to_chat()

    async def subscribe_to_chat(self) -> None:
        if self._chat_subscribed:
            return

        subscription = eventsub.ChatMessageSubscription(
            broadcaster_user_id=self.broadcaster_id,
            user_id=self.bot_id,
        )

        result = await self.subscribe_websocket(
            subscription,
            token_for=self.bot_id,
        )

        self._chat_subscribed = True
        logger.info("Подписка на чат создана: %s", result)

    async def event_message(
        self,
        payload: twitchio.ChatMessage,
    ) -> None:
        print(
            f"[TWITCH CHAT] [{payload.broadcaster.name}] "
            f"{payload.chatter.name}: {payload.text}",
            flush=True,
        )

        logger.info(
            "[%s] %s: %s",
            payload.broadcaster.name,
            payload.chatter.name,
            payload.text,
        )

        guess = extract_guess(payload.text)
        if guess is None:
            return

        result = await self.game_store.submit_guess(
            guess,
            user_id=str(payload.chatter.id),
            user_name=payload.chatter.name,
        )

        if result is GuessResult.INCORRECT:
            print("[TWITCH GAME] Неправильно", flush=True)
        elif result is GuessResult.WON:
            print(
                f"[TWITCH GAME] Правильно! Победитель: {payload.chatter.name}",
                flush=True,
            )

    async def event_oauth_authorized(
        self,
        payload: twitchio.authentication.UserTokenPayload,
    ) -> None:
        await self.add_token(
            payload.access_token,
            payload.refresh_token,
        )

        # Сохранить сразу, не ждать остановки приложения.
        await self.save_tokens()

        logger.info(
            "OAuth выполнен, токен сохранён: user_id=%s",
            payload.user_id,
        )

        if payload.user_id == self.bot_id:
            await self.subscribe_to_chat()
