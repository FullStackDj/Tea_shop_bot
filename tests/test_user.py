import pytest
from unittest.mock import AsyncMock
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from handlers.menu_processing import get_menu_content
from handlers.user_private import user_private_router, add_to_cart, OrderForm


@pytest.mark.asyncio
async def test_start_command(mocker):
    mock_get_menu_content = mocker.patch('handlers.menu_processing.get_menu_content',
                                         return_value=('mock_media', 'mock_reply_markup'))

    message = AsyncMock(types.Message)
    message.answer_photo = AsyncMock()

    await user_private_router.message.handlers[0].callback(message, AsyncMock())

    message.answer_photo.assert_called_with('mock_media', caption='mock_media', reply_markup='mock_reply_markup')
    mock_get_menu_content.assert_called_once()


@pytest.mark.asyncio
async def test_add_to_cart(mocker):
    mock_orm_add_user = mocker.patch('database.orm_query.orm_add_user', AsyncMock())
    mock_orm_add_to_cart = mocker.patch('database.orm_query.orm_add_to_cart', AsyncMock())

    callback = AsyncMock(CallbackQuery)
    callback.from_user.id = 1
    callback.from_user.first_name = 'John'
    callback.from_user.last_name = 'Doe'
    callback_data = AsyncMock()
    callback_data.product_id = 123

    session = AsyncMock()

    await add_to_cart(callback, callback_data, session)

    mock_orm_add_user.assert_called_once_with(session, user_id=1, first_name='John', last_name='Doe', phone=None)
    mock_orm_add_to_cart.assert_called_once_with(session, user_id=1, product_id=123)
