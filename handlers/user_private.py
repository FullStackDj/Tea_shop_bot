from aiogram import F, types, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import (
    as_list,
    as_marked_section,
    Bold,
)

from filters.chat_types import ChatTypeFilter

from key_boards.reply import get_keyboard

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        'Hello, I am a virtual assistant',
        reply_markup=get_keyboard(
            'Menu',
            'About the store',
            'Payment options',
            'Shipping options',
            placeholder='What are you interested in?',
            sizes=(2, 2)
        ),
    )


@user_private_router.message(or_f(Command('menu'), (F.text.lower() == 'menu')))
async def menu_cmd(message: types.Message):
    await message.answer('Here is the menu:')


@user_private_router.message(F.text.lower() == 'about the store')
@user_private_router.message(Command('about'))
async def about_cmd(message: types.Message):
    await message.answer('About us:')


@user_private_router.message(F.text.lower() == 'payment options')
@user_private_router.message(Command('payment'))
async def payment_cmd(message: types.Message):
    text = as_marked_section(
        Bold('Payment options:'),
        'Card in the bot',
        'Cash on delivery/card',
        'At the establishment',
        marker='✅ ',
    )
    await message.answer(text.as_html())


@user_private_router.message(
    (F.text.lower().contains('delivery')) | (F.text.lower() == 'shipping options'))
@user_private_router.message(Command('shipping'))
async def menu_cmd(message: types.Message):
    text = as_list(
        as_marked_section(
            Bold('Shipping/order options:'),
            'Courier',
            'Self-pickup (I will come and get it)',
            'I will eat at your place (I will come now)',
            marker='✅ ',
        ),
        as_marked_section(
            Bold('Not allowed:'),
            'Mail',
            'Pigeons',
            marker='❌ '
        ),
        sep='\n----------------------\n',
    )
    await message.answer(text.as_html())
