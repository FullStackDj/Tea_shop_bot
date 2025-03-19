import asyncio
import environ
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeAllPrivateChats

from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from common.bot_commands_list import private

env = environ.Env()
environ.Env.read_env()

ALLOWED_UPDATES = ['message, edited_message']

bot = Bot(token=env('TOKEN'), parse_mode=ParseMode.HTML)
dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(user_group_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


asyncio.run(main())
