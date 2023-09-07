from http import HTTPStatus

from aiogram import Bot, F, Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from logger import logger
from middlewares.role import IsGuestMessageMiddleware
from service.access import (AccessCallbackFactory, access_action,
                            access_request_builder)
from service.message import send_message_to_admin
from utils import get_api_answer, patch_api_answer
from validators import check_full_name, check_phone_number

router = Router()
router.message.middleware(IsGuestMessageMiddleware())


class Access(StatesGroup):
    name = State()
    phone = State()


@router.message(Text('Заявка'))
async def access(
        message: types.Message,
        state: FSMContext
):
    answer = get_api_answer(f'users/{message.from_user.id}')
    data = answer.json()
    builder = InlineKeyboardBuilder()
    if not data['request_for_access']:
        text = ("Для получения доступа напишите свое Имя Фамилию \n"
                "Пример: Иван Иванов")
        await state.set_state(Access.name)
        builder.button(
            text='Отмена',
            callback_data=AccessCallbackFactory(
                action=access_action.stop)
        )
    else:
        text = ('Ваша заявка на рассмотрении \n'
                f'Имя: {data["fullname"]} \n'
                f'Телефон: {data["phone_number"]}')
        builder.button(
            text='Отменить заявку',
            callback_data=AccessCallbackFactory(
                action=access_action.request_remove)
        )
    await message.answer(
        text,
        reply_markup=builder.as_markup()
    )


@router.message(Access.name)
async def callbacks_request_name(
        message: Message,
        state: FSMContext,
        bot: Bot):
    builder = await access_request_builder()
    fullname = message.text

    if not check_full_name(fullname):
        text = ('Введите имя и фамилию в правильно формате \n'
                'Пример: Иван Иванов')
        await message.answer(
            text,
            reply_markup=builder.as_markup()
        )
        await state.set_state(Access.name)
        return
    text = ("А так же требуется ваш номер телефона \n"
            "Пример: +79781234567")
    fullname = fullname.split(' ')
    await state.update_data(first_name=fullname[0],
                            last_name=fullname[1])
    await message.answer(
        text,
        reply_markup=builder.as_markup()
    )
    await state.set_state(Access.phone)


@router.message(Access.phone)
async def callbacks_request_phone(
        message: Message,
        state: FSMContext,
        bot: Bot):
    builder = await access_request_builder()
    number = check_phone_number(message.text)
    if not number:
        await message.answer(
            "Введите номер телефона в правильном формате \n"
            "Пример: +79781234567",
            reply_markup=builder.as_markup()
        )
        await state.set_state(Access.phone)
        return
    await state.update_data(phone=number)
    data = await state.get_data()
    await state.clear()
    patch_api_answer(f'users/{message.from_user.id}/',
                     data={
                         'first_name': data['first_name'],
                         'last_name': data['last_name'],
                         'phone_number': data['phone'],
                         'request_for_access': True
                     })
    await message.answer(
        'Ваша заявка отправлена!'
    )
    await send_message_to_admin(
        f'Появилась новая заявка от пользователя {data["fullname"]}')


@router.callback_query(
    AccessCallbackFactory.filter(F.action == access_action.stop)
)
async def callbacks_request_stop(
        callback: types.CallbackQuery,
        callback_data: AccessCallbackFactory,
        state: FSMContext
):
    await state.clear()
    text = 'Подача заявки отменена'
    await callback.message.edit_text(
        text
    )


@router.callback_query(
    AccessCallbackFactory.filter(F.action == access_action.request_remove)
)
async def callbacks_request_remove(
        callback: types.CallbackQuery,
        callback_data: AccessCallbackFactory,
        state: FSMContext
):
    response = patch_api_answer(f'users/{callback.from_user.id}/',
                                data={
                                    'request_for_access': False
                                })
    data = response.json()
    if response.status_code == HTTPStatus.OK:
        logger.info(f'{data["fullname"]} отменил заявку на доступ')
    else:
        logger.error('Произошла обишка при отмене заявки \n'
                     f'{data}')
    text = 'Подача заявки отменена'
    await callback.message.edit_text(
        text
    )
