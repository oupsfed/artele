import json
import os
from http import HTTPStatus
from pathlib import Path

import requests
from aiogram import Bot
from dotenv import load_dotenv
from logger import logger
from requests import Response

load_dotenv()

BASE_DIR = Path(__file__).resolve()

DEBUG = True

URL = os.getenv('URL')

if DEBUG:
    URL = os.getenv('URL_DEV')

HEADERS = {'Content-type': 'application/json',
           'Content-Encoding': 'utf-8'}
token = os.getenv('TOKEN')
bot = Bot(token=token, parse_mode='HTML')