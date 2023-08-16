from aiogram.exceptions import TelegramBadRequest

from bot.logger import logger
from bot.utils import bot, get_api_answer
from bot.validators import check_user_exist


async def send_message_to_user(user_id: int,
                               text: str):
    """
    Отправка сообщения пользователю

            Parameters:
                    user_id (int) : telegram-chat-id пользователя
                    text (str) : Текст сообщения
            Returns:
                    text (str): Возвращает строку об успехе или ошибке
    """
    user = await check_user_exist(user_id)
    if not user:
        return 'Пользователь не найден'
    user_name = user['name']
    try:
        await bot.send_message(
            chat_id=user_id,
            text=text
        )
        text = f'Сообщение успешно отправлено пользователю {user_name}'
        logger.debug(text)
    except TelegramBadRequest:
        text = f'Сообщение не отправлено! пользователь {user_name} не найден'
        logger.error(text)
    return text


async def send_message_to_admin(text):
    """
    Отправка сообщения администраторам

            Parameters:
                    text (str) : Текст сообщения
            Returns:
                    text (str): Возвращает строку об успехе или ошибке
    """
    admin_data = get_api_answer('admin/').json()
    for admin in admin_data:
        await send_message_to_user(
            admin['telegram_chat_id'],
            text
        )
