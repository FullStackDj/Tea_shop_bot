import pytest
from unittest.mock import MagicMock, AsyncMock
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from handlers.admin_private import admin_router, AddProduct
from database.orm_query import orm_get_categories, orm_add_product, orm_delete_product


@pytest.fixture
def mock_db():
    mock = MagicMock()
    mock.orm_get_categories = AsyncMock(
        return_value=[MagicMock(id=1, name='Category 1'), MagicMock(id=2, name='Category 2')]
    )
    mock.orm_get_products = AsyncMock(
        return_value=[MagicMock(id=1, name='Product 1', description='Description 1', price=100, image='image_url')]
    )
    mock.orm_delete_product = AsyncMock()
    mock.orm_change_banner_image = AsyncMock()
    mock.orm_add_product = AsyncMock()
    mock.get_keyboard = AsyncMock(return_value='keyboard_mock')
    mock.get_callback_btns = AsyncMock(return_value='callback_btns_mock')
    return mock


@pytest.fixture
def mock_fsm_context():
    fsm_context = MagicMock(FSMContext)
    fsm_context.set_state = AsyncMock()
    fsm_context.get_state = AsyncMock(return_value=None)
    fsm_context.update_data = AsyncMock()
    fsm_context.clear = AsyncMock()
    return fsm_context


@pytest.mark.asyncio
async def test_admin_command(mock_db):
    message = MagicMock()
    message.answer = AsyncMock()

    await admin_router.message(message)

    message.answer.assert_called_once_with('What would you like to do?', reply_markup=mock_db.get_keyboard.return_value)


@pytest.mark.asyncio
async def test_product_assortment(mock_db):
    message = MagicMock()
    message.answer = AsyncMock()

    await admin_router.message(message)

    mock_db.orm_get_categories.assert_called_once()
    message.answer.assert_called_once_with('Choose a category', reply_markup=mock_db.get_callback_btns.return_value)


@pytest.mark.asyncio
async def test_show_products_in_category(mock_db):
    callback = MagicMock()
    callback.message.answer_photo = AsyncMock()
    callback.message.answer = AsyncMock()
    callback.answer = AsyncMock()

    await admin_router.callback_query(callback)

    mock_db.orm_get_products.assert_called_once_with(1)
    callback.message.answer_photo.assert_called_once_with(
        'image_url',
        caption='<strong>Product 1</strong>\nDescription 1\nPrice: 100',
        reply_markup=mock_db.get_callback_btns.return_value,
        parse_mode=ParseMode.HTML
    )
    callback.message.answer.assert_called_once_with('OK, here is the list of products ⏫')
    callback.answer.assert_called_once()


@pytest.mark.asyncio
async def test_delete_product(mock_db):
    callback = MagicMock()
    callback.answer = AsyncMock()
    callback.message.answer = AsyncMock()

    await admin_router.callback_query(callback)

    mock_db.orm_delete_product.assert_called_once_with(1)
    callback.answer.assert_called_once_with('Product deleted')
    callback.message.answer.assert_called_once_with('Product deleted!')


@pytest.mark.asyncio
async def test_add_banner(mock_db, mock_fsm_context):
    message = MagicMock()
    message.answer = AsyncMock()

    message.photo = [MagicMock(file_id='photo_id')]
    message.caption = 'Category 1'

    await admin_router.message(message, mock_fsm_context)

    mock_db.orm_change_banner_image.assert_called_once_with('Category 1', 'photo_id')
    message.answer.assert_called_once_with('Banner added/updated.')


@pytest.mark.asyncio
async def test_add_product(mock_db, mock_fsm_context):
    message = MagicMock()
    message.answer = AsyncMock()

    await admin_router.message(message, mock_fsm_context)

    mock_db.orm_add_product.assert_called_once_with({
        'name': 'Product Name',
        'description': 'Product Description',
        'category': '1',
        'price': '100',
        'image': 'photo_id'
    })
    message.answer.assert_called_once_with('Product added/updated', reply_markup=mock_db.get_keyboard.return_value)


@pytest.mark.asyncio
async def test_back_step(mock_db, mock_fsm_context):
    message = MagicMock()
    message.answer = AsyncMock()

    await admin_router.message(message, mock_fsm_context)

    message.answer.assert_called_once_with('Ok, you have returned to the previous step \n Enter the description again:')
