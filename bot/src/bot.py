import json

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, filters
from aiogram.utils import executor
import aiohttp
import os
import typing as tp
import random
from yarl import URL
import uuid
from collections import OrderedDict
from database import DataBaseHandler
import argparse
from dotenv import load_dotenv

from pathlib import Path

local_path = Path(__file__).resolve()
load_dotenv(dotenv_path=local_path.parent.parent / ".env")

bot = Bot(token=os.environ['BOT_TOKEN'])
dp = Dispatcher(bot)

__PARAMS: dict[str, tp.Any] = {
    'LANGUAGE': 'ru',
    'SIZE': '595x842',
    'START_GIF': URL('https://media.tenor.com/0NkVlanL1DcAAAAd/american-psycho.gif'),
    'NOT_FOUND_GIFS': (URL('https://media.tenor.com/GxA2qm-qmlkAAAAd/'
                           'meme-american-psycho.gif'),
                       URL('https://media.tenor.com/wz24kdz6aU8AAAAC/'
                           'bateman-patrick-bateman.gif'),
                       URL('https://media.tenor.com/H_3UxRMa1HUAAAAd/'
                           'patrick-bateman-american-psycho.gif')),
    'BAD_REQUEST_GIF': URL('https://tenor.com/view/ryan-gosling-blade-'
                           'runner2049-defeat-sad-disappointed-gif-17817916'),

    'MORE_INFO_FIELDS': (('Release date: ', 'releaseDate'),
                         ('Countries: ', 'countries'), ('Plot: ', 'plot'),
                         ('Plot local: ', 'plotLocal'), ('Awards: ', 'awards'),
                         ('Writers: ', 'writers'), ('Languages: ', 'languages')),
    'CALLBACK_KEY': (uuid.uuid4().hex + uuid.uuid4().hex)[:32],
    'LRU_MAX_SIZE': 256,
    'GOOGLE_SEARCH_URL': URL('https://www.googleapis.com/customsearch/v1'),
    'DATABASE_NAME': 'user_history_db'  # os.environ['DATABASE_NAME']
}

__KEYBOARDS: dict[str, types.InlineKeyboardMarkup] = {
    'empty_kbd': types.InlineKeyboardMarkup(),
}

__FILM_INFO_DICT: OrderedDict[str, tp.Any] = OrderedDict()
__DATABASE = DataBaseHandler(__PARAMS['DATABASE_NAME'])


# START
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):  # type: ignore
    await message.answer('[ ]({}){}'.format(None, 'Привет! Я бот Traveline, задай мне свой вопрос'),
                         parse_mode='markdown', reply_markup=__KEYBOARDS['empty_kbd'])

    await bot_help(message)


# HELP
@dp.message_handler(commands=['help'])
async def bot_help(message: types.Message):  # type: ignore
    await message.answer('Чтобы задать вопрос, просто напишите и отправьте его мне\n'
                         '/start для старта/рестарта бота\n'
                         '/help для помощи\n'
                         '/history для истории запросов\n'
                         )

# HISTORY
@dp.message_handler(commands=['history'])
async def user_search_history(message: types.Message):  # type: ignore
    history_list: list[tp.Any] = await __DATABASE.user_search_history(message.from_user.id)
    history_str: str = '\n'.join(map(lambda h: h[0], history_list))
    await message.answer(text=history_str if history_str else 'No history')

# BAD REQUEST CASE
async def bad_request(message: types.Message):  # type: ignore
    await message.answer('[ ]({}){}'.format(__PARAMS['BAD_REQUEST_GIF'],
                                            'Простите, произошла какая-то ошибкана сервере'),
                         parse_mode='markdown', reply_markup=__KEYBOARDS['empty_kbd'])


# IF FILM WAS NOT FOUND IN IMDb
async def not_found(message: types.Message) -> None:
    await message.answer("[ ]({}){}".format(random.choice(__PARAMS['NOT_FOUND_GIFS']),
                                            'Ого, я не знаю ответа на этот вопрос'),
                         parse_mode='markdown', reply_markup=__KEYBOARDS['empty_kbd'])


# REQUEST PROCESSER
@dp.message_handler()
async def film(message: types.Message):  # type: ignore
    async with aiohttp.ClientSession() as session:
        jj = {"data": message.text}
        response = await session.post(url=f'http://server-search_system:5055/search', json=jj)
    
        if response.status != 200:
            await bad_request(message)
        elif not (results := (await response.json())):
            await not_found(message)
        else:

            await message.answer("[ ]({}){}".format(None, results), parse_mode='markdown'),  # reply_markup=keyboard)
            await __DATABASE.append(message.from_user.id, f'Q: {message.text}\nA: {results}')


if __name__ == '__main__':
    executor.start_polling(dp)