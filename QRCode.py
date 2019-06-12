import os

import requests
from settings import LT_URL, QR_PATH, MONGODB
from uuid import uuid4
import time, hashlib


def create_QR(num):
    qr_list = []
    for i in range(num):
        qr_info = f'{time.time()}{uuid4()}{time.time()}'
        qr_code = hashlib.md5(qr_info.encode('utf-8')).hexdigest()
        res = requests.get(LT_URL % qr_code)
        qr_img = os.path.join(QR_PATH, f'{qr_code}.jpg')
        with open(qr_img, 'wb') as f:
            f.write(res.content)
        qr = {'device_key': qr_code}
        qr_list.append(qr)
        time.sleep(0.1)
    MONGODB.devices.insert_many(qr_list)


if __name__ == '__main__':
    create_QR(5)
