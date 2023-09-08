from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from magic_filter import F

from core import request_api
from logger import logger
from middlewares.role import is_admin
from service.food import (FoodCallbackFactory, food_action, food_builder,
                          food_info, menu_builder)

router = Router()

MAIN_MESSAGE = 'Меню:'


@router.message(Text('Меню'))
async def menu(message: types.Message,
               state: FSMContext, ):
    await state.clear()
    builder = await menu_builder(
        request_api.get('api/food/').json(),
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
    food = request_api.get(f'/api/food/{callback_data.id}/').json()
    cart = request_api.get('/api/cart/',
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
        callback_data: FoodCallbackFactory,
        state: FSMContext,
):
    await state.clear()
    builder = await menu_builder(
        request_api.get('api/food/',
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


@router.callback_query(FoodCallbackFactory.filter(F.action == food_action.add_to_cart))
async def callbacks_add_to_cart(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory
):
    user_id = callback.from_user.id
    food_id = callback_data.id
    cart = request_api.post('api/cart/',
                            data={
                                'user': user_id,
                                'food': food_id
                            }).json()
    builder = await food_builder(
        cart=cart,
        food=cart['food'],
        page=callback_data.page,
        admin=is_admin(user_id)
    )
    await callback.message.edit_reply_markup(
        reply_markup=builder.as_markup()
    )


@router.callback_query(FoodCallbackFactory.filter(F.action == food_action.remove_from_cart))
async def callbacks_remove_from_cart(
        callback: types.CallbackQuery,
        callback_data: FoodCallbackFactory
):
    user_id = callback.from_user.id
    food_id = callback_data.id
    cart = request_api.get('api/cart/',
                           params={
                               'user': user_id,
                               'food': food_id
                           }).json()
    cart = cart['results'][0]
    cart = request_api.delete(f'api/cart/{cart["id"]}').json()
    builder = await food_builder(
        cart=cart,
        food=cart['food'],
        page=callback_data.page,
        admin=is_admin(user_id)
    )
    try:
        await callback.message.edit_reply_markup(
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest:
        logger.info('Пользователь пытается сделать '
                    'количетсво продуктов отрицательным')
