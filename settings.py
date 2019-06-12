# 数据库配置
from pymongo import MongoClient

MC = MongoClient('127.0.0.1', 27017)
MONGODB = MC['music']

from redis import Redis

REDIS_DB = Redis('127.0.0.1', 6379, db=6)

# 目录配置
MUSIC_PATH = 'Music'
PICTURE_PATH = 'Picture'
QR_PATH = 'QRCode'
VOICE_PATH = 'Chats'

# Restful

RET = {
    'code': 0,
    'msg': '',
    'data': {}
}

# 联图二维码
LT_URL = 'http://qr.liantu.com/api.php?text=%s'

# 百度AI配置
from aip import AipSpeech

""" 你的 APPID AK SK """
APP_ID = '16027552'
API_KEY = 'ydZfy8GRB7Bz02UGeaXh4hGE'
SECRET_KEY = 'zUbGAD21x4I6abGYhwo9jAfERCZzeGpA'

SPEECH_CLIENT = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

VOICE = {
    'vol': 5,
    'spd': 6,
    'pit': 7,
    'per': 4
}

# 图灵机器人配置
# url就是图灵的街口,图灵官网:tuling123.com,可以查看接入教程
TULING_URL = 'http://openapi.tuling123.com/openapi/api/v2'
TULING_DATA = {
    "perception": {
        "inputText": {
            "text": ""
        },
    },
    "userInfo": {
        "apiKey": "34b2c01332074b2b9d9293f72547df39",
        "userId": ""
    }
}
