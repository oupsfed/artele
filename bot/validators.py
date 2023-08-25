import re
from http import HTTPStatus
from typing import Union

from utils import get_api_answer


async def check_user_exist(user_id: int) -> Union[bool, dict]:
    """
    Валидатор проверки существования пользователя

            Parameters:
                    user_id (int) : telegram-chat-id пользователя

            Returns:
                    answer (bool, dict): Возвращает либо
                    данные о пользователе либо False
    """
    answer = get_api_answer(f'users/{user_id}')
    if answer.status_code == HTTPStatus.OK:
        return answer.json()
    return False


def check_permissions(user_id: int) -> bool:
    """
    Валидатор проверки прав администратора пользователя

            Parameters:
                    user_id (int) : telegram-chat-id пользователя

            Returns:
                    answer (bool): возвращает bool ответ
    """
    answer = get_api_answer(f'users/{user_id}')
    return answer.json()['is_staff']


def check_phone_number(number: str) -> Union[bool, int]:
    """
    Валидатор проверки корректности ввода номера

            Parameters:
                    number (str) : строка номера телефона

            Returns:
                    answer (bool, int): Возвращает либо
                    номер либо False
    """
    replace_data = [
        '+', ' ', '(', ')', '-'
    ]
    for replace_symbol in replace_data:
        number = number.replace(replace_symbol, '')
    if number[0] == '7':
        number = f'8{number[1:]}'
    if number.isdigit():
        return number
    return False


def check_full_name(fullname: str):
    if not re.search('[А-Яа-я]{1,16} [А-Яа-я]{1,16}', fullname):
        return False
    return True
