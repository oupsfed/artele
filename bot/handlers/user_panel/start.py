from aiogram import Router, types
from aiogram.filters import KICKED, ChatMemberUpdatedFilter, Command
from aiogram.types import ChatMemberUpdated
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from logger import logger
from middlewares.role import is_admin, is_guest
from service.user import user_create
from utils import delete_api_answer

router = Router()


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    user = message.chat
    await user_create(
        telegram_chat_id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        user_name=user.username
    )
    text = 'Бот находится в стадии разработки'
    btn_text = 'Заказ'
    if is_guest(user.id):
        btn_text = 'Заявка'
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Меню"),
        types.KeyboardButton(text='Корзина'),
    )
    builder.row(
        types.KeyboardButton(text=btn_text),
        types.KeyboardButton(text="Информация"),
    )
    if is_admin(user.id):
        builder.row(
            types.KeyboardButton(text='Панель администратора'),
        )

    await message.answer(text,
                         parse_mode='HTML',
                         reply_markup=builder.as_markup(resize_keyboard=True))


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated):
    logger.info(f'Пользователь {event.from_user.first_name} '
                f'{event.from_user.last_name} chat_id - {event.from_user.id}'
                f' заблокировал бота')
    delete_api_answer(f'users/{event.from_user.id}')
