# from aiogram import Bot, types, Dispatcher, filters
# from aiogram.utils import 
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
    # 'GOOGLE_API_KEY': os.environ['GOOGLE_API_KEY'],
    # 'GOOGLE_CX_KEY': os.environ['GOOGLE_CX_KEY'],
    # 'IMDB_API_KEY': os.environ['IMDB_API_KEY'],
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
                         #  '/stat for showing your searching stats\n'
                         '/history для истории запросов\n'
                         #  f'/language allow user to switch between '
                         #  f'two search languages russian (ru) and english (en). '
                         #  f'will affect content of additional information about films'
                         )


# # STATISTICS
# @dp.message_handler(commands=['stat'])
# async def user_stat(message: types.Message):  # type: ignore
#     stats: list[tuple[str, str]] = await __DATABASE.user_stats(message.from_user.id)
#     pairs: str = '\n'.join([f'{title}: {count}' for title, count in stats])
#     await message.answer(text=pairs if pairs else 'No stats yet, make some requests please')


# HISTORY
@dp.message_handler(commands=['history'])
async def user_search_history(message: types.Message):  # type: ignore
    history_list: list[tp.Any] = await __DATABASE.user_search_history(message.from_user.id)
    history_str: str = '\n'.join(map(lambda h: h[0], history_list))
    await message.answer(text=history_str if history_str else 'No history')


# LANGUAGE
# @dp.message_handler(commands=['language'])
# async def switch_language(message: types.Message):  # type: ignore
#     __PARAMS['LANGUAGE'] = 'en' if __PARAMS['LANGUAGE'] == 'ru' else 'ru'
#     await message.answer(f'Language was switched to {__PARAMS["LANGUAGE"]}')


# BAD REQUEST CASE
async def bad_request(message: types.Message):  # type: ignore
    await message.answer('[ ]({}){}'.format(__PARAMS['BAD_REQUEST_GIF'],
                                            'Запрос не распознан'),
                         parse_mode='markdown', reply_markup=__KEYBOARDS['empty_kbd'])


# IF FILM WAS NOT FOUND IN IMDb
async def not_found(message: types.Message) -> None:
    await message.answer("[ ]({}){}".format(random.choice(__PARAMS['NOT_FOUND_GIFS']),
                                            'Ого, я не знаю ответа на этот вопрос'),
                         parse_mode='markdown', reply_markup=__KEYBOARDS['empty_kbd'])


# # GET FILM SHORT INFO (this will be shown in reply on request)
# async def get_film_info(response: aiohttp.ClientResponse) -> dict[str, tp.Any]:
#     res: dict[str, tp.Any] = (await response.json())
#     return {'short_info': f'Title: {res["fullTitle"]}\n'
#                           f'Type: {res["type"]}\n'
#                           f'Runtime: {res["runtimeStr"]}\n'
#                           f'IMDb Rating: {res["imDbRating"]}\n'
#                           f'Directors: {res["directors"]}\n'
#                           f'Stars: {res["stars"]}',
#             'image_url': URL(f'https://imdb-api.com/API/ResizeImage?apiKey='
#                              f'{__PARAMS["IMDB_API_KEY"]}&size={__PARAMS["SIZE"]}'
#                              f'&url={res["image"]}'),
#             'full_info': res}


# # INFO FOR MORE INFO
# async def get_more_info(info: dict[str, tp.Any]) -> str:
#     res: list[str] = [f'  {info["fullTitle"]}  ']
#     for key, value in __PARAMS['MORE_INFO_FIELDS']:
#         if value != 'plotLocal' and info[value]:
#             res.append(key + info[value])
#         elif __PARAMS['LANGUAGE'] != 'en' and info[value]:
#             res.append(key + info[value])
#     return '\n'.join(res)


# # INLINE-BUTTONS
# @dp.callback_query_handler(filters.Text(startswith=__PARAMS['CALLBACK_KEY']))
# async def more_info_call(callback: types.CallbackQuery):  # type: ignore
#     key: str = callback.data[32:-3]
#     type_: str = callback.data[-3:]
#     __FILM_INFO_DICT.move_to_end(key, last=True)  # YEAH, LRU :^)
#     if type_ == 'inf':
#         await callback.message.answer(text=__FILM_INFO_DICT[key][0])
#     elif type_ == 'u_1':
#         await callback.message.answer(text=__FILM_INFO_DICT[key][1])
#     elif type_ == 'u_2':
#         await callback.message.answer(text=__FILM_INFO_DICT[key][2])
#     await callback.answer()


# # FILM LINKS
# async def get_film_links(info: dict[str, tp.Any], session: aiohttp.ClientSession) -> tuple[URL, URL]:
#     params = {'q': f'{info["full_info"]["fullTitle"]} смотреть онлайн',
#               'cx': __PARAMS['GOOGLE_CX_KEY'],
#               'key': __PARAMS['GOOGLE_API_KEY']}
#     response = await session.get(url=__PARAMS['GOOGLE_SEARCH_URL'], params=params)
#     data = await response.json()
#     url_1 = URL(data['items'][0]['link'])
#     url_2 = URL(data['items'][1]['link'])
#     return url_1, url_2


# REQUEST PROCESSER
@dp.message_handler()
async def film(message: types.Message):  # type: ignore
    async with aiohttp.ClientSession() as session:
        response = await session.post(url=f'server-search_system:5055/search', data=message.text)

        if response.status_code != 200:
            await bad_request(message)
        elif not (results := (await response.json())['results']):
            await not_found(message)
        else:
            # film_id: str = results[0]['id']
            # results = await session.get(url=f'https://imdb-api.com/{__PARAMS["LANGUAGE"]}/'
            #                                 f'API/Title/{__PARAMS["IMDB_API_KEY"]}/{film_id}')
            # info = await get_film_info(results)
            # key = uuid.uuid4().hex[:29]
            # film_info = await get_more_info(info['full_info'])
            # url_1, url_2 = await get_film_links(info, session)
            # __FILM_INFO_DICT[key] = (film_info, url_1, url_2)
            # if len(__FILM_INFO_DICT) > __PARAMS['LRU_MAX_SIZE']:  # YEAH, LRU :^)
            #     __FILM_INFO_DICT.popitem(last=False)
            # keyboard = types.InlineKeyboardMarkup(row_width=3)
            # keyboard.add(types.InlineKeyboardButton(text='More info',
            #                                         callback_data=f'{__PARAMS["CALLBACK_KEY"]}{key}inf'))
            # keyboard.add(types.InlineKeyboardButton(text=f'Watch on {url_1.host}', url=str(url_1),
            #                                         callback_data=f'{__PARAMS["CALLBACK_KEY"]}{key}u_1'))
            # keyboard.add(types.InlineKeyboardButton(text=f'Watch on {url_2.host}', url=str(url_2),
            #                                         callback_data=f'{__PARAMS["CALLBACK_KEY"]}{key}u_2'))

            await message.answer("({}){}".format(response.text), parse_mode='markdown'),  # reply_markup=keyboard)
            await __DATABASE.append(message.from_user.id, f'Q: {message.text}\nA: {response.text}')


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(prog='Bot', description='Invoking telegram bot')
    # parser.add_argument('--env', type=str, required=True, help='path to .env file')
    # args = parser.parse_args()
    # load_dotenv(path=args['--env'])
    # dp.start_polling()
    executor.start_polling(dp)