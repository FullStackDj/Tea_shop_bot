from aiogram import F, types, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import (
    orm_add_to_cart,
    orm_add_user,
)

from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from key_boards.inline import MenuCallBack, get_user_main_btns

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name='main')

    await message.answer_photo(media.media, caption=media.caption, reply_markup=reply_markup)


async def add_to_cart(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    user = callback.from_user
    await orm_add_user(
        session,
        user_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=None,
    )
    await orm_add_to_cart(session, user_id=user.id, product_id=callback_data.product_id)
    await callback.answer('Product added to cart.')


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession):
    if callback_data.menu_name == 'add_to_cart':
        await add_to_cart(callback, callback_data, session)
        return

    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


class OrderForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_phone = State()
    waiting_for_delivery = State()
    waiting_for_payment = State()
    confirm_order = State()


@user_private_router.callback_query(MenuCallBack.filter(F.menu_name == 'order'), StateFilter(None))
async def order_callback(callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession,
                         state: FSMContext):
    await callback.answer('Let\'s start the order process. What is your name?')
    await state.set_state(OrderForm.waiting_for_name)


@user_private_router.message(OrderForm.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text

    await state.update_data(name=name)
    await message.answer('Now enter your surname.')
    await state.set_state(OrderForm.waiting_for_surname)


@user_private_router.message(OrderForm.waiting_for_surname)
async def process_surname(message: types.Message, state: FSMContext):
    surname = message.text

    await state.update_data(surname=surname)
    await message.answer('Enter your phone number.')
    await state.set_state(OrderForm.waiting_for_phone)


@user_private_router.message(OrderForm.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text

    await state.update_data(phone=phone)
    await message.answer('Choose a delivery method (for example, "Courier" or "Pickup").')
    await state.set_state(OrderForm.waiting_for_delivery)


@user_private_router.message(OrderForm.waiting_for_delivery)
async def process_delivery(message: types.Message, state: FSMContext):
    delivery_method = message.text

    await state.update_data(delivery_method=delivery_method)
    await message.answer('Now choose a payment method (for example, "Cash" or "Card").')
    await state.set_state(OrderForm.waiting_for_payment)


@user_private_router.message(OrderForm.waiting_for_payment)
async def process_payment(message: types.Message, state: FSMContext):
    payment_method = message.text
    await state.update_data(payment_method=payment_method)

    user_data = await state.get_data()
    name = user_data['name']
    surname = user_data['surname']
    phone = user_data['phone']
    delivery_method = user_data['delivery_method']
    payment_method = user_data['payment_method']

    confirmation_message = f'Your order:\nName: {name}\nSurname: {surname}\nPhone: {phone}\n' \
                           f'Delivery method: {delivery_method}\nPayment method: {payment_method}\n' \
                           'Confirm the order. If everything is correct, write "Confirm".'
    await message.answer(confirmation_message)
    await state.set_state(OrderForm.confirm_order)


@user_private_router.message(OrderForm.confirm_order)
async def confirm_order(message: types.Message, state: FSMContext):
    if message.text.lower() == 'confirm':
        user_data = await state.get_data()

        await orm_add_user(
            session,
            user_id=message.from_user.id,
            first_name=user_data['name'],
            last_name=user_data['surname'],
            phone=user_data['phone'],
        )

        await message.answer('Your order has been successfully placed! We will contact you for confirmation.')
        await state.clear()
    else:
        await message.answer('If you want to change the information, send the command \'/start\'.')
