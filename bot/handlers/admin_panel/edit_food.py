from aiogram import Bot, F, Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.actions import food_action
from core.factories import FoodCallbackFactory
from middlewares.role import IsAdminMessageMiddleware, is_admin
from service.food import (FOOD_COL, admin_edit_food_builder, encode_image,
                          food_builder, food_info, menu_builder)
from utils import delete_api_answer, get_api_answer, patch_api_answer

MAIN_MESSAGE = 'Меню'

router = Router()
router.message.middleware(IsAdminMessageMiddleware())


class EditFood(StatesGroup):
    name = State()


@router.message(Text('Редактирование меню'))
async def admin_menu(message: types.Message):
    builder = await menu_builder(user_id=message.from_user.id)

    await message.answer(
        MAIN_MESSAGE,
        reply_markup=builder.as_markup()
    )


@router.callback_query(FoodCallbackFactory.filter(F.action == food_action.update_preview))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory
):
    builder = await admin_edit_food_builder(
        food_id=callback_data.id,
        page=callback_data.page
    )
    await callback.message.edit_reply_markup(
        reply_markup=builder.as_markup()
    )


@router.callback_query(
    FoodCallbackFactory.filter(F.action == food_action.update_column))
async def callbacks_edit_food(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory,
        state: FSMContext
):
    await state.update_data(id=callback_data.id,
                            col=callback_data.column)
    await callback.message.answer(
        text=f'Введите (Пришлите) {FOOD_COL[callback_data.column]}'
    )
    await state.set_state(EditFood.name)


@router.message(EditFood.name)
async def callbacks_edit_food_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    data = await state.get_data()
    if data['col'] == 'image':
        photo = message.photo[-1]
        direction = f"tmp/{photo.file_id}.jpg"
        await bot.download(
            photo,
            destination=direction
        )
        encode_data = await encode_image(direction)
        data['name'] = encode_data
    else:
        await state.update_data(name=message.text)
        data = await state.get_data()
    await state.clear()
    food = patch_api_answer(f'food/{data["id"]}/',
                            data={
                                data['col']: data['name']
                            }).json()
    cart = get_api_answer('cart/',
                          params={
                              'user': message.from_user.id,
                              'food': food['id']
                          }).json()
    food_data = await food_info(food)
    builder = await food_builder(
        cart=cart,
        food=food,
        admin=is_admin(message.from_user.id)
    )
    await message.answer_photo(
        food_data['image'],
        caption=(f'{FOOD_COL[data["col"]]} успешно изменено \n'
                 f'{food_data["text"]}'),
        reply_markup=builder.as_markup()
    )


@router.callback_query(FoodCallbackFactory.filter(F.action == food_action.remove_preview))
async def callbacks_delete_food(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Удалить',
        callback_data=FoodCallbackFactory(
            action=food_action.remove,
            id=callback_data.id)
    )
    builder.button(
        text='Отмена',
        callback_data=FoodCallbackFactory(
            action=food_action.get,
            id=callback_data.id)
    )
    await callback.message.edit_reply_markup(
        reply_markup=builder.as_markup()
    )


@router.callback_query(FoodCallbackFactory.filter(F.action == food_action.remove))
async def callbacks_delete_food(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory
):
    delete_api_answer(f'food/{callback_data.id}')
    await callback.message.answer(
        'Товар успешно удален')
    await callback.message.delete()
