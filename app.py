import environ
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import asyncio

env = environ.Env()
environ.Env.read_env()

bot = Bot(token=env('TOKEN'))
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Start')


@dp.message()
async def echo(message: types.Message):
    await message.answer(message.text)


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
