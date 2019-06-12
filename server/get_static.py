import os

from flask import Blueprint, send_file
from settings import RET, PICTURE_PATH, MUSIC_PATH, VOICE_PATH, QR_PATH

get_static = Blueprint('get_static', __name__)


@get_static.route('/getimage/<filename>')
def get_image(filename):
    file_path = os.path.join(PICTURE_PATH, filename)
    return send_file(file_path)


@get_static.route('/getmusic/<filename>')
def get_music(filename):
    file_path = os.path.join(MUSIC_PATH, filename)
    return send_file(file_path)


@get_static.route('/getchat/<filename>')
def get_chat(filename):
    file_path = os.path.join(VOICE_PATH, filename)
    return send_file(file_path)


@get_static.route('/qrcode/<filename>')
def qrcode(filename):
    file_path = os.path.join(QR_PATH, filename)
    return send_file(file_path)
