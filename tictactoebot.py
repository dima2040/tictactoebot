import asyncio
import logging
import os

from aiogram import F, Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command

from tictactoebot import *
from tictactoebot.modules.inline_queries import router as InlineQueriesRouter
from tictactoebot.modules.callback_queries import router as CallbackQueriesRouter
from tictactoebot.modules.commands import router as  CommandsRouter

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()



async def main():
    dp.include_router(InlineQueriesRouter)
    dp.include_router(CallbackQueriesRouter)
    dp.include_router(CommandsRouter)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
