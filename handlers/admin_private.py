from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode

from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter, IsAdmin
from key_boards.reply import get_keyboard
from database.orm_query import orm_get_products, orm_delete_product, orm_get_product, orm_update_product
from key_boards.inline import get_callback_btns

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())

ADMIN_KB = get_keyboard(
    'Add product',
    'Assortment',
    placeholder='Choose action',
    sizes=(2,),
)


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()

    product_for_change = None

    texts = {
        'AddProduct:name': 'Enter the name again:',
        'AddProduct:description': 'Enter the description again:',
        'AddProduct:price': 'Enter the price again:',
        'AddProduct:image': 'This is the last state, so...',
    }


@admin_router.message(Command('admin'))
async def add_product(message: types.Message):
    await message.answer('What do you want to do?', reply_markup=ADMIN_KB)


@admin_router.message(F.text == 'Assortment')
async def starring_at_product(message: types.Message, session: AsyncSession):
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f'<strong>{product.name}</strong>\n{product.description}\nPrice: {round(product.price, 2)}',
            reply_markup=get_callback_btns(
                btns={
                    'Delete': f'delete_{product.id}',
                    'Change': f'change_{product.id}',
                }
            ),
            parse_mode=ParseMode.HTML
        )
    await message.answer('OK, here is the list of products')


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split('_')[-1]
    await orm_delete_product(session, int(product_id))

    await callback.answer('Product deleted')
    await callback.message.answer('Product deleted!')


@admin_router.callback_query(StateFilter(None), F.data.startswith('change_'))
async def change_product_callback(
        callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split('_')[-1]

    product_for_change = await orm_get_product(session, int(product_id))

    AddProduct.product_for_change = product_for_change

    await callback.answer()
    await callback.message.answer(
        'Enter the product name', reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter(None), F.text == 'Add product')
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        'Enter the product name', reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter('*'), Command('cancel'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'cancel')
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await state.clear()
    await message.answer('Actions canceled', reply_markup=ADMIN_KB)


@admin_router.message(StateFilter('*'), Command('back'))
@admin_router.message(StateFilter('*'), F.text.casefold() == 'back')
async def back_step_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()

    if current_state == AddProduct.name:
        await message.answer("There is no previous step. Please enter the product name or type 'cancel'.")
        return

    previous = None

    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f'Okay, you have returned to the previous step. \n{AddProduct.texts[previous.state]}')
            return

        previous = step


@admin_router.message(AddProduct.name, or_f(F.text, F.text == '.'))
async def add_name(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        if len(message.text) >= 100:
            await message.answer(
                'The product name should not exceed 100 characters. \n Please enter again'
            )
            return

        await state.update_data(name=message.text)
    await message.answer('Enter the product description')
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer('You entered invalid data, please enter the product name')


@admin_router.message(AddProduct.description, or_f(F.text, F.text == '.'))
async def add_description(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        await state.update_data(description=message.text)
    await message.answer('Enter the product price')
    await state.set_state(AddProduct.price)


@admin_router.message(AddProduct.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer('You entered invalid data, please enter the product description')


@admin_router.message(AddProduct.price, or_f(F.text, F.text == '.'))
async def add_price(message: types.Message, state: FSMContext):
    if message.text == '.':
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer('Please enter a valid price')
            return

        await state.update_data(price=message.text)
    await message.answer('Upload the product image')
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer('You entered invalid data, please enter the product price')


@admin_router.message(AddProduct.image, or_f(F.photo, F.text == '.'))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == '.':
        await state.update_data(image=AddProduct.product_for_change.image)
    else:
        await state.update_data(image=message.photo[-1].file_id)
    data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(session, data)
        await message.answer('The product has been added/modified', reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(
            f'Error: \n{str(e)}\n',
            reply_markup=ADMIN_KB,
        )
        await state.clear()

    AddProduct.product_for_change = None


@admin_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer('Please send the product photo')
