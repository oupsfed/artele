from aiogram import Bot, F, Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from middlewares.role import IsAdminMessageMiddleware
from service.message import send_message_to_user
from service.user_list import (UserListCallbackFactory, user_block,
                               user_list_actions, user_list_builder,
                               user_list_get_builder, user_list_get_info)
from utils import get_api_answer

router = Router()
router.message.middleware(IsAdminMessageMiddleware())


class SendMessage(StatesGroup):
    direct = State()
    all = State()


@router.message(Text('Оповещение пользователей'))
async def user_list(message: types.Message):
    builder = await user_list_builder()
    await message.answer(
        'Список авторизированных пользователей',
        reply_markup=builder.as_markup()
    )


@router.callback_query(UserListCallbackFactory.filter(F.action == user_list_actions.get))
async def callbacks_show_request(
        callback: types.CallbackQuery,
        callback_data: UserListCallbackFactory
):
    text = await user_list_get_info(callback_data.user_id)
    builder = await user_list_get_builder(callback_data.user_id,
                                          callback_data.page)
    await callback.message.edit_reply_markup(
        text,
        reply_markup=builder.as_markup()
    )


@router.callback_query(UserListCallbackFactory.filter(F.action == user_list_actions.remove))
async def callbacks_accept_request(
        callback: types.CallbackQuery,
        callback_data: UserListCallbackFactory,
        bot: Bot
):
    text = await user_block(callback_data.user_id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Назад',
        callback_data=UserListCallbackFactory(
            action=user_list_actions.get_all,
            page=callback_data.page)
    )
    builder.adjust(1)
    await callback.message.answer(text,
                                  reply_markup=builder.as_markup())
    await callback.message.delete()


@router.callback_query(UserListCallbackFactory.filter(F.action == user_list_actions.get_all))
async def callbacks_accept_request(
        callback: types.CallbackQuery,
        callback_data: UserListCallbackFactory,
        bot: Bot
):
    builder = await user_list_builder(callback_data.user_id)
    await callback.message.edit_reply_markup(
        'Список авторизированных пользователей',
        reply_markup=builder.as_markup()
    )


@router.callback_query(UserListCallbackFactory.filter(F.action == user_list_actions.send_direct))
async def callbacks_send_message(
        callback: types.CallbackQuery,
        callback_data: UserListCallbackFactory,
        state: FSMContext
):
    await callback.message.answer(
        text='Введите сообщение',
    )
    await callback.message.delete()
    await state.update_data(user_id=callback_data.user_id)
    await state.set_state(SendMessage.direct)


@router.callback_query(UserListCallbackFactory.filter(F.action == user_list_actions.send_to_all))
async def callbacks_send_message(
        callback: types.CallbackQuery,
        callback_data: UserListCallbackFactory,
        state: FSMContext
):
    await callback.message.answer(
        text='Введите сообщение',
    )
    await state.set_state(SendMessage.all)


@router.message(SendMessage.direct)
async def callbacks_send_message_direct(
        message: Message,
        state: FSMContext,
        bot: Bot):
    data = await state.get_data()
    text = await send_message_to_user(
        user_id=data['user_id'],
        text=message.text
    )
    await state.clear()
    await message.answer(text)


@router.message(SendMessage.all)
async def callbacks_send_message_all(
        message: Message,
        state: FSMContext,
        bot: Bot):
    answer = get_api_answer('users/authorize/').json()
    success = []
    for user in answer:
        text = await send_message_to_user(user['telegram_chat_id'],
                                          message.text)
        success.append(text)
    await state.clear()
    if len(success) > 0:
        await message.answer('\n'.join(success))
