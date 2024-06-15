import asyncio
import logging.config

from aiogram import Bot, Dispatcher

from tictactoebot.config import BOT_TOKEN, LOGGING_CONFIG
from tictactoebot.inline_queries import router as InlineQueriesRouter
from tictactoebot.callback_queries import router as CallbackQueriesRouter
from tictactoebot.commands import router as CommandsRouter


async def main() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(InlineQueriesRouter)
    dp.include_router(CallbackQueriesRouter)
    dp.include_router(CommandsRouter)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
