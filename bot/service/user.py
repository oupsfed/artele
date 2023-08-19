from http import HTTPStatus

from logger import logger
from utils import post_api_answer
from validators import check_user_exist


async def user_create(telegram_chat_id: int,
                      first_name: str,
                      last_name: str,
                      user_name: str):
    user = await check_user_exist(telegram_chat_id)
    if user:
        logger.warning(f'{first_name} {last_name} уже зарегистрирован')
        return user
    register = post_api_answer('users/',
                               data={
                                   'telegram_chat_id': telegram_chat_id,
                                   'first_name': first_name,
                                   'last_name': last_name,
                                   'username': user_name
                               })
    if register.status_code == HTTPStatus.CREATED:
        logger.info(f'Зарегистрирован новый пользователь: {first_name} {last_name}')
        return user
    logger.error(f'Произошла ошибка при регистрации пользователя: {register.json()}')
    return False
