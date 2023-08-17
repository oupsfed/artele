from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from middlewares.role import IsAdminMessageMiddleware
from service.food import (FoodCallbackFactory, add_food_builder,
                          download_and_encode_image, food_action,
                          food_builder, food_info)
from utils import post_api_answer

MAIN_MESSAGE = 'Меню'

router = Router()
router.message.middleware(IsAdminMessageMiddleware())


class AddFood(StatesGroup):
    name = State()
    description = State()
    weight = State()
    price = State()
    image = State()


@router.callback_query(FoodCallbackFactory.filter(F.action == food_action.create_preview))
async def callbacks_add_food_name(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory,
        state: FSMContext
):
    builder = await add_food_builder()
    await callback.message.answer(
        text='Введите название товара',
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddFood.name)


@router.message(AddFood.name)
async def callbacks_add_food_description(
        message: Message,
        state: FSMContext
):
    await state.update_data(name=message.text)
    builder = await add_food_builder()
    await message.answer(
        text='Введите описание товара',
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddFood.description)


@router.message(AddFood.description)
async def callbacks_add_food_weight(
        message: Message,
        state: FSMContext
):
    await state.update_data(description=message.text)
    builder = await add_food_builder()
    await message.answer(
        text='Введите вес товара в граммах',
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddFood.weight)


@router.message(AddFood.weight)
async def callbacks_add_food_price(
        message: Message,
        state: FSMContext,
):
    await state.update_data(weight=message.text)
    builder = await add_food_builder()
    await message.answer(
        text='Введите цену товара',
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddFood.price)


@router.message(AddFood.price)
async def callbacks_add_food_image(
        message: Message,
        state: FSMContext,
        bot: Bot):
    await state.update_data(price=message.text)
    builder = await add_food_builder()
    await message.answer(
        text='Добавьте фото товара',
        reply_markup=builder.as_markup()
    )
    await state.set_state(AddFood.image)


@router.message(AddFood.image)
async def callbacks_add_food_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    image_string = await download_and_encode_image(message.photo[-2])
    await state.update_data(image=image_string)
    data = await state.get_data()
    answer = post_api_answer('food/',
                             data=data)
    food = answer.json()
    food_id = food['id']
    food_data = await food_info(food_id)
    builder = await food_builder(
        message.from_user.id,
        food_id
    )
    await message.answer_photo(
        food_data['image'],
        caption=food_data['text'],
        reply_markup=builder.as_markup()
    )
