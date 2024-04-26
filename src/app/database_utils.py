import logging
import os

from database_accessor import DatabaseAccessor

DATABASE_CONFIG = {
    'host': os.getenv('PG_HOST'),
    'port': os.getenv('PG_PORT'),
    'database_name': os.getenv('PG_DIGEST_DB_NAME'),
    'user': os.getenv('PG_USER'),
    'password': os.getenv('PG_USER_PASS'),
}

database_accessor = DatabaseAccessor(DATABASE_CONFIG)

GET_TITLE_ANSWER = \
    f'''
    SELECT *
    FROM title_answer
    '''

GET_ALL_TITLES = \
    f'''
    SELECT title
    FROM title_answer
    '''

GET_ANSWER = \
    f'''
    SELECT title
    FROM title_answer
    WHERE TITLE = %(title)s
    '''

CREATE_TITLE_ANSWER = \
    f'''
    CREATE TABLE title_answer(
        title varchar constraint firstkey PRIMARY KEY,
        answer varchar   
    );
    '''

FETCH_RECORD = \
    f'''
    INSERT INTO title_answer(title, answer)
    VALUES (%(title)s, %(answer)s)
    '''

def create_title_answer(logger: logging):
    with database_accessor.connect(logger) as connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TITLE_ANSWER)

def get_all_elements(logger: logging) -> dict:
    with database_accessor.connect(logger) as connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_TITLE_ANSWER)
            result = cursor.fetchall()
            data_dict = {}

            # Проходимся по каждой строке результата
            for row in result:
                title = row[0]  # Первый столбец - title
                answer = row[1]  # Второй столбец - answer

                # Добавляем пару ключ-значение в словарь
                data_dict[title] = answer

            return data_dict

def get_answer(title: str, logger: logging) -> str:
    with database_accessor.connect(logger) as connection:
        with connection.cursor() as cursor:
            bind_variables = {'title': title}
            cursor.execute(GET_ANSWER, bind_variables)
            result = cursor.fetchone()

            if result:
                # Если есть результат, извлекаем значение из первого столбца (так как запрос SELECT title ...)
                answer = result[0]
                return answer
            else:
                # Если результат пуст, возвращаем пустую строку или None, в зависимости от вашего выбора
                return ""


def get_all_titles(logger: logging) -> list:
    with database_accessor.connect(logger) as connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_ALL_TITLES)
            result = cursor.fetchall()

            # Преобразуем список кортежей в список строк
            titles = [row[0] for row in result]

            return titles

def fetch_all(records: dict, logger:logging):
    with database_accessor.connect(logger) as connection:
        with connection.cursor() as cursor:
            for k, v in records.items():
                bind_variables = {'title': k, 'answer': v}
                cursor.execute(FETCH_RECORD, bind_variables)
                connection.commit()
