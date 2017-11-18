from os import environ
from re import sub
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


def clean_host(host):
    regex = '^https?://'
    return sub(regex, '', host)


# Load env variables
DEV = environ.get('DEV', False)
PORT = environ.get('PORT')
HOST = environ.get('HOST')
RAW_HOST = clean_host(HOST) # no http?s
SSL_ENABLED = HOST.find('https') >= 0
CLIENT_ID = environ.get('CLIENT_ID')
CLIENT_SECRET = environ.get('CLIENT_SECRET')
DEFAULTIMGURL = 'http://image.boomsbeat.com/data/images/full/595/bill-gates-jpg.jpg'
PGDB = environ.get('PGDB')
PGUSER = environ.get('PGUSER')
DB_HOST = environ.get('DB_HOST_DOCKER') or RAW_HOST
API_KEY_BING = environ.get('API_KEY_BING')
API_KEY_FACE = environ.get('API_KEY_FACE')
API_KEY_VISION = environ.get('API_KEY_VISION')
IMAGE_SERVER_HOST = environ.get('IMAGE_SERVER_BASE')

if DEV == 'TRUE':
    SSL = {
        'cert': 'ssl/dev/server.crt',
        'key': 'ssl/dev/server.key'
    }
else:
    SSL = {
        'cert': 'ssl/prod/fullchain.pem',
        'key': 'ssl/prod/privkey.pem'
    }
    # e.g. timeshark.org:8000
