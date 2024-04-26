import sqlite3 as sq
from typing import Any


class DataBaseHandler:
    def __init__(self, sqlite_database_name: str):
        self.connection = sq.connect(sqlite_database_name)
        self.connection.execute('CREATE TABLE IF NOT EXISTS requests(id INTEGER PRIMARY KEY '
                                'AUTOINCREMENT, username TEXT, qa TEXT)')
        self.connection.commit()

    async def append(self, *data):
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO requests (username, qa) VALUES'
                       ' (?, ?)', data)
        self.connection.commit()

    # async def user_stats(self, username: str) -> list[Any]:
    #     cursor = self.connection.cursor()
    #     return cursor.execute('SELECT title, COUNT(title) AS freq FROM requests WHERE '
    #                           'username == :uname GROUP BY qa ORDER BY freq DESC',
    #                           {'uname': username}).fetchall()

    async def user_search_history(self, username: str) -> list[Any]:
        cursor = self.connection.cursor()
        return cursor.execute('SELECT qa FROM requests'
                              ' WHERE username == :uname',
                              {'uname': username}).fetchall()