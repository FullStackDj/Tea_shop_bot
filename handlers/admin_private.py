from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter

from filters.chat_types import ChatTypeFilter, IsAdmin
from key_boards.reply import get_keyboard

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())

ADMIN_KB = get_keyboard(
    'Add product',
    'Edit product',
    'Delete product',
    'I just came to look around',
    placeholder='Choose action',
    sizes=(2, 1, 1),
)


@admin_router.message(Command('admin'))
async def add_product(message: types.Message):
    await message.answer('What do you want to do?', reply_markup=ADMIN_KB)


@admin_router.message(F.text == 'I just came to look around')
async def starring_at_product(message: types.Message):
    await message.answer('OK, here is the list of products')


@admin_router.message(F.text == 'Edit product')
async def change_product(message: types.Message):
    await message.answer('OK, here is the list of products')


@admin_router.message(F.text == 'Delete product')
async def delete_product(message: types.Message):
    await message.answer('Choose product(s) to delete')


class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    image = State()

    texts = {
        'AddProduct:name': 'Enter the name again:',
        'AddProduct:description': 'Enter the description again:',
        'AddProduct:price': 'Enter the price again:',
        'AddProduct:image': 'This is the last state, so...',
    }


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


@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Enter the product description')
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def add_name2(message: types.Message, state: FSMContext):
    await message.answer('You entered invalid data, please enter the product name')


@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('Enter the product price')
    await state.set_state(AddProduct.price)


@admin_router.message(AddProduct.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer('You entered invalid data, please enter the product description')


@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await message.answer('Upload the product image')
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer('You entered invalid data, please enter the product price')


@admin_router.message(AddProduct.image, F.photo)
async def add_image(message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await message.answer('Product added', reply_markup=ADMIN_KB)
    data = await state.get_data()
    await message.answer(str(data))
    await state.clear()


@admin_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer('Please send the product photo')
