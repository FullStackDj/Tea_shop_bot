from aiogram import F, types, Router
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_add_to_cart,
    orm_add_user,
)

from filters.chat_types import ChatTypeFilter
from key_boards.inline import get_callback_btns

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer('Hello, I am your virtual assistant',
                         reply_markup=get_callback_btns(btns={
                             'Click me': 'some_1'
                         }))


@user_private_router.callback_query(F.data.startswith('some_'))
async def counter(callback: types.CallbackQuery):
    number = int(callback.data.split('_')[-1])

    await callback.message.edit_text(
        text=f'Clicks - {number}',
        reply_markup=get_callback_btns(btns={
            'Click again': f'some_{number + 1}'
        }))
