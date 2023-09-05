import json
import os
from http import HTTPStatus
from sys import stdout
from typing import Optional

import requests
from aiogram import Bot
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from dotenv import load_dotenv
from logger import logger
from requests import Response

load_dotenv()

DEBUG = True

URL = os.getenv('URL')

if DEBUG:
    URL = os.getenv('URL_DEV')


HEADERS = {'Content-type': 'application/json',
           'Content-Encoding': 'utf-8'}
token = os.getenv('TOKEN')
bot = Bot(token=token, parse_mode='HTML')


class Action:
    get = 'get'
    create = 'create'
    remove = 'remove'
    get_all = 'get_all'
    update = 'update'

    def __init__(self,
                 callback_name):
        self.callback = callback_name
        self.get = self.callback + self.get
        self.create = self.callback + self.create
        self.remove = self.callback + self.remove
        self.get_all = self.callback + self.get_all
        self.update = self.callback + self.update

    def __str__(self):
        return self.callback


class ArteleCallbackData(CallbackData, prefix='artele'):
    action: str
    page: Optional[int] = 1
    back_data: Optional[CallbackData]


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


async def paginate_builder(json_response: dict,
                           builder,
                           callback_factory,
                           action):
    page_buttons = 0
    page = json_response['page']
    if json_response['previous']:
        builder.button(
            text="⬅️",
            callback_data=callback_factory(
                action=action,
                page=page - 1
            )
        )
        page_buttons += 1
    if json_response['next']:
        builder.button(
            text="➡️",
            callback_data=callback_factory(
                action=action,
                page=page + 1
            )
        )
        page_buttons += 1
    return page_buttons, builder
