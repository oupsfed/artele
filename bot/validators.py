from http import HTTPStatus

from bot.utils import get_api_answer


async def check_user_exist(user_id: int):
    answer = get_api_answer(f'users/{user_id}')
    if answer.status_code == HTTPStatus.OK:
        return answer.json()
    return False


def check_permissions(user_id: int) -> bool:
    answer = get_api_answer(f'users/{user_id}')
    return answer.json()['is_staff']


def check_phone_number(number: str) -> str:
    replace_data = [
        '+', ' ', '(', ')', '-'
    ]
    for replace_symbol in replace_data:
        number = number.replace(replace_symbol, '')
    if number[0] == '7':
        number = f'8{number[1:]}'
    return number
