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


def check_endpoint(endpoint: str) -> str:
    """
    Проверка наличия ошибок при совмещении URL и эндпоинт
    """
    if URL[-1] != '/' and endpoint[0] != '/':
        endpoint = f'/{endpoint}'
        logger.warning('URL и endpoint не содержат /')
    if URL[-1] == '/' and endpoint[0] == '/':
        endpoint = endpoint[1:]
        logger.warning('URL и endpoint содержат двойной /')
    endpoint = endpoint + '/'
    endpoint = endpoint.replace('//', '/')
    return URL + endpoint


def get(endpoint: str,
        params=None) -> Response:
    """
    Делает GET запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    params (dict) : параметры запроса

            Returns:
                    answer (Response): Информация с API-сервиса
    """
    endpoint = check_endpoint(endpoint)
    answer = requests.get(
        url=endpoint,
        headers=HEADERS,
        params=params
    )
    if answer.status_code != HTTPStatus.OK:
        logger.error(f'Запрос к {endpoint} отклонен')
    return answer


def post(endpoint: str,
         data: dict) -> Response:
    """
    Делает POST запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    data (dict): данные для отправки на API

            Returns:
                    answer (Response): Информация с API-сервиса
    """
    endpoint = check_endpoint(endpoint)
    data = json.dumps(data)
    return requests.post(
        url=endpoint,
        data=data,
        headers=HEADERS
    )


def patch(endpoint: str,
          data: dict) -> Response:
    """
    Делает PATCH запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    data (dict): данные для отправки на API

            Returns:
                    answer (Response): Информация с API-сервиса
    """
    endpoint = check_endpoint(endpoint)
    data = json.dumps(data)
    return requests.patch(
        url=endpoint,
        data=data,
        headers=HEADERS
    )


def delete(endpoint: str) -> Response:
    """
    Делает DELETE запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа

            Returns:
                   answer (Response): Информация с API-сервиса
    """
    endpoint = check_endpoint(endpoint)
    return requests.delete(
        url=endpoint,
        headers=HEADERS,
    )
