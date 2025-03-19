from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from filters.chat_types import ChatTypeFilter

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('12345')


@user_private_router.message(or_f(Command('menu')))
async def menu_cmd(message: types.Message):
    await message.answer('menu:')


@user_private_router.message(F.text.lower() == 'about us')
@user_private_router.message(Command('about'))
async def menu_cmd(message: types.Message):
    await message.answer('about:')


@user_private_router.message(F.text.lower() == 'payment options')
@user_private_router.message(Command('payment'))
async def menu_cmd(message: types.Message):
    await message.answer('payment:')


@user_private_router.message(F.text.lower().contains('deliver') | (F.text.lower() == 'delivery options'))
@user_private_router.message(Command('shipping'))
async def menu_cmd(message: types.Message):
    await message.answer('shipping and delivery:')
