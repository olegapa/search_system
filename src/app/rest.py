import logging
import os.path
import sys

import requests
from flask import Flask, request
from main import SearchEngine
from database_utils import create_title_answer, fetch_all, get_all_elements
from database_accessor import DatabaseAccessor

# ELASTIC_HOST = os.getenv('ELASTIC_HOST')
# ELASTIC_USER = os.getenv('ELASTIC_USER')
# ELASTIC_USER_PASS = os.getenv('ELASTIC_USER_PASS')
#
OK_STATUS = {
    'status': 'success',
    'status_code': 200
}
#
logger = logging.getLogger(__name__)
# basic = requests.auth.HTTPBasicAuth(ELASTIC_USER, ELASTIC_USER_PASS)
#
#
app = Flask(__name__)
#

engine = SearchEngine("/app/src/sourses/data")
# create_title_answer(logger)
DATABASE_CONFIG = {
    'host': os.getenv('PG_HOST'),
    'port': os.getenv('PG_PORT'),
    'database_name': os.getenv('PG_DIGEST_DB_NAME'),
    'user': os.getenv('PG_USER'),
    'password': os.getenv('PG_USER_PASS'),
}

database_accessor = DatabaseAccessor(DATABASE_CONFIG)

@app.route('/search', methods=['POST'])
def search():
    data = get_all_elements(logger)
    answer = engine(request.json["data"], data=data)
    return OK_STATUS

@app.route('/init', methods=['POST'])
def init():
    create_title_answer(logger)
    fetch_all({t: c["content"] for t, c in engine.titles.items()},
              logger)
    return OK_STATUS

if __name__ == '__main__':
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(levelname)s]........ %(message)s ........'))
    log.addHandler(handler)
    app.run(
        port=5055,
        host='0.0.0.0'
    )
