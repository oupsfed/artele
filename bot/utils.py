import json
import os
from http import HTTPStatus

import requests
from aiogram import Bot
from dotenv import load_dotenv
from requests import Response

from logger import logger

load_dotenv()

DEBUG = True

URL = os.getenv('URL')

if DEBUG:
    URL = os.getenv('URL_DEV')

HEADERS = {'Content-type': 'application/json',
           'Content-Encoding': 'utf-8'}
token = os.getenv('TOKEN')
bot = Bot(token=token, parse_mode='HTML')


def get_api_answer(endpoint: str,
                   params=None) -> Response:
    """
    Делает GET запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    params (dict) : параметры запроса

            Returns:
                    answer (Response): Информация с API-сервиса
    """
    endpoint = f'{URL}api/{endpoint}'
    answer = requests.get(
        url=endpoint,
        headers=HEADERS,
        params=params
    )
    if answer.status_code != HTTPStatus.OK:
        logger.error(f'Запрос к {endpoint} отклонен')
    return answer


def post_api_answer(endpoint: str,
                    data: dict) -> Response:
    """
    Делает POST запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    data (dict): данные для отправки на API

            Returns:
                    answer (Response): Информация с API-сервиса
    """
    endpoint = f'{URL}api/{endpoint}'
    data = json.dumps(data)
    return requests.post(
        url=endpoint,
        data=data,
        headers=HEADERS
    )


def patch_api_answer(endpoint: str,
                     data: dict) -> Response:
    """
    Делает PATCH запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    data (dict): данные для отправки на API

            Returns:
                    answer (Response): Информация с API-сервиса
    """
    endpoint = f'{URL}api/{endpoint}'
    data = json.dumps(data)
    return requests.patch(
        url=endpoint,
        data=data,
        headers=HEADERS
    )


def delete_api_answer(endpoint: str) -> Response:
    """
    Делает DELETE запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа

            Returns:
                   answer (Response): Информация с API-сервиса
    """
    endpoint = f'{URL}api/{endpoint}'
    return requests.delete(
        url=endpoint,
        headers=HEADERS,
    )
