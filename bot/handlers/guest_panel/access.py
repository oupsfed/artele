from aiogram import Bot, Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from middlewares.role import IsGuestMessageMiddleware
from service.message import send_message_to_admin
from utils import patch_api_answer
from validators import check_phone_number

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
    await message.answer(
        "Для получения доступа напишите свое Имя Фамилию \n"
        "Пример: Иван Иванов"
    )
    await state.set_state(Access.name)


@router.message(Access.name)
async def callbacks_edit_food_name_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    await state.update_data(name=message.text)
    await message.answer(
        "А так же требуется ваш номер телефона \n"
        "Пример: +79781234567"
    )
    await state.set_state(Access.phone)


@router.message(Access.phone)
async def callbacks_edit_food_name_confirm(
        message: Message,
        state: FSMContext,
        bot: Bot):
    number = check_phone_number(message.text)
    if not number:
        await message.answer(
            "Введите номер телефона в правильном формате \n"
            "Пример: +79781234567"
        )
        await state.set_state(Access.phone)
        return
    await state.update_data(phone=number)
    data = await state.get_data()
    await state.clear()
    patch_api_answer(f'users/{message.from_user.id}/',
                     data={
                         'name': data['name'],
                         'phone_number': data['phone'],
                         'request_for_access': True
                     })
    await message.answer(
        'Ваша заявка отправлена!'
    )
    await send_message_to_admin(
        bot,
        f'Появилась новая заявка от пользователя {data["name"]}')
