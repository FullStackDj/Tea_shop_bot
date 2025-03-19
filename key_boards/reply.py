from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Menu'),
            KeyboardButton(text='About us'),
        ],
        [
            KeyboardButton(text='Shipping'),
            KeyboardButton(text='Payment'),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder='Whaaaaaaaaaat?'
)

delete_kb = ReplyKeyboardRemove()
