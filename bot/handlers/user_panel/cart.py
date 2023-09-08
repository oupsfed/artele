from aiogram import Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder
from magic_filter import F

from core import request_api
from logger import logger
from service.cart import CartCallbackFactory, cart_action, cart_builder
from service.food import food_info
from utils import get_api_answer

router = Router()

MAIN_MESSAGE = 'Корзина:'


@router.message(Text('Корзина'))
async def menu(message: types.Message):
    user_id = message.from_user.id
    cart = request_api.get(
        'api/cart/',
        params={
            'user': user_id,
        }).json()
    total_price = get_api_answer(
        f'cart/{user_id}/sum/'
    ).json()
    builder = await cart_builder(
        json_response=cart,
        total_price=total_price['total']
    )
    await message.answer(
        MAIN_MESSAGE,
        reply_markup=builder.as_markup()
    )


@router.callback_query(CartCallbackFactory.filter(F.action == cart_action.get_all))
async def callbacks_show_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    user_id = callback.from_user.id
    cart = request_api.get(
        'api/cart/',
        params={
            'user': user_id,
            'page': callback_data.page
        }).json()
    total_price = request_api.get(
        f'api/cart/{user_id}/sum/'
    ).json()
    builder = await cart_builder(
        json_response=cart,
        total_price=total_price['total']
    )
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            MAIN_MESSAGE,
            reply_markup=builder.as_markup()
        )
    else:
        await callback.message.edit_reply_markup(
            reply_markup=builder.as_markup()
        )


@router.callback_query(CartCallbackFactory.filter(F.action == cart_action.get))
async def callbacks_show_food(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    food_data = await food_info(callback_data.food_id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Назад',
        callback_data=CartCallbackFactory(
            action=cart_action.get_all,
            page=callback_data.page
        ))
    builder.adjust(1)
    await callback.message.answer_photo(
        food_data['image'],
        caption=food_data['text'],
        reply_markup=builder.as_markup()
    )
    await callback.message.delete()


@router.callback_query(CartCallbackFactory.filter(F.action == cart_action.create))
async def callbacks_add_to_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    user_id = callback.from_user.id
    food_id = callback_data.food_id
    request_api.post('api/cart/',
                     data={
                         'user': user_id,
                         'food': food_id
                     }).json()
    cart_data = request_api.get('api/cart/',
                                params={
                                    'user': user_id,
                                    'page': callback_data.page
                                }).json()
    total_price = request_api.get(f'api/cart/{user_id}/sum').json()
    builder = await cart_builder(
        json_response=cart_data,
        total_price=total_price['total']
    )
    await callback.message.edit_reply_markup(
        reply_markup=builder.as_markup()
    )


@router.callback_query(CartCallbackFactory.filter(F.action == cart_action.remove))
async def callbacks_delete_from_cart(
        callback: types.CallbackQuery,
        callback_data: CartCallbackFactory
):
    user_id = callback.from_user.id
    food_id = callback_data.food_id
    cart = request_api.get('api/cart/',
                           params={
                               'user': user_id,
                               'food': food_id
                           }).json()
    cart = cart['results'][0]
    request_api.delete(f'api/cart/{cart["id"]}')
    cart_data = request_api.get('api/cart/',
                                params={
                                    'user': user_id,
                                    'page': callback_data.page
                                }).json()
    total_price = request_api.get(f'api/cart/{user_id}/sum').json()
    builder = await cart_builder(
        json_response=cart_data,
        total_price=total_price['total']
    )
    try:
        await callback.message.edit_reply_markup(
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest:
        logger.info('Пользователь пытается сделать '
                    'количетсво продуктов отрицательным')
