from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Text
from logger import logger
from magic_filter import F
from service.cart import add_to_cart, cart_action, remove_from_cart
from service.food import (FoodCallbackFactory, food_action, food_builder,
                          food_info, menu_builder)
from utils import get_api_answer
from middlewares.role import is_admin


router = Router()

MAIN_MESSAGE = 'Меню:'


@router.message(Text('Меню'))
async def menu(message: types.Message):
    builder = await menu_builder(
        get_api_answer('food/').json(),
        admin=is_admin(message.from_user.id)
    )
    await message.answer(
        MAIN_MESSAGE,
        reply_markup=builder.as_markup()
    )


@router.callback_query(FoodCallbackFactory.filter(F.action == food_action.get))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory
):
    user_id = callback.from_user.id
    food = get_api_answer(f'food/{callback_data.food_id}/').json()
    cart = get_api_answer(f'cart/',
                          params={
                              'user': user_id,
                              'food': food['id']
                          }).json()
    food_data = await food_info(food)
    builder = await food_builder(cart=cart,
                                 food=food,
                                 admin=is_admin(user_id))
    await callback.message.answer_photo(
        food_data['image'],
        caption=food_data['text'],
        reply_markup=builder.as_markup()
    )
    await callback.message.delete()


@router.callback_query(FoodCallbackFactory.filter(F.action == food_action.get_all))
async def callbacks_show_page(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory
):
    # builder = await menu_builder(page=callback_data.page,
    #                              user_id=callback.from_user.id)
    builder = await menu_builder(
        get_api_answer('food/',
                       params={
                           'page': callback_data.page
                       }).json(),
        admin=is_admin(callback.from_user.id)
    )
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            MAIN_MESSAGE,
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_reply_markup(
            MAIN_MESSAGE,
            reply_markup=builder.as_markup()
        )


@router.callback_query(FoodCallbackFactory.filter(F.action == cart_action.create))
async def callbacks_add_to_cart(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory
):
    user_id = callback.from_user.id
    food_id = callback_data.food_id
    await add_to_cart(
        user_id=user_id,
        food_id=food_id
    )
    builder = await food_builder(
        user_id=user_id,
        food_id=food_id,
        page=callback_data.page
    )
    await callback.message.edit_reply_markup(
        reply_markup=builder.as_markup()
    )


@router.callback_query(FoodCallbackFactory.filter(F.action == cart_action.remove))
async def callbacks_remove_from_cart(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory
):
    user = callback.from_user
    food_id = callback_data.food_id
    await remove_from_cart(
        user.id,
        food_id
    )
    builder = await food_builder(
        callback.from_user.id,
        food_id,
        callback_data.page
    )
    try:
        await callback.message.edit_reply_markup(
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest:
        logger.info('Пользователь пытается сделать '
                    'количетсво продуктов отрицательным')
