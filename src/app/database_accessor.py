import logging

import psycopg2


class DatabaseAccessor:

    def __init__(self, database_config: dict) -> None:
        self._host = database_config['host']
        self._port = database_config['port']
        self._database_name = database_config['database_name']
        self._user = database_config['user']
        self._password = database_config['password']
        self._connection = None

    def connect(self, logger: logging):
        if not self._connection or self._connection.closed:
            logger.info('Connecting to %s...', self._host)
            self._connection = psycopg2.connect(host=self._host,
                                                port=self._port,
                                                dbname=self._database_name,
                                                user=self._user,
                                                password=self._password)
        return self._connection
