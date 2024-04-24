import logging
import os.path
import sys

import requests
from flask import Flask, request


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

@app.route('/search', methods=['POST'])
def language():
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
