import os
import time

import requests
from settings import MONGODB, MUSIC_PATH, PICTURE_PATH
from uuid import uuid4

TikTokMusic = 'https://www.ximalaya.com/revision/play/album?albumId=14963542&pageNum=1&sort=-1&pageSize=30'
# 要抓取数据的网址的头,为了防止反扒需要模仿改请求头
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
}


def data_collect(tar):
    # 模仿请求头
    res = requests.get(TikTokMusic, headers=header)
    # print(res.json())
    music_list = []
    for music_info in res.json().get('data').get('tracksAudioPlay'):
        print(music_info.get('trackName'), music_info.get('src'))
        music = requests.get(music_info.get('src'))
        picture = requests.get('http:' + music_info.get('trackCoverPath'))
        filename = uuid4()
        music_file = os.path.join(MUSIC_PATH, f'{filename}.mp3')
        picture_file = os.path.join(PICTURE_PATH, f'{filename}.jpg')

        with open(music_file, 'wb') as f:
            f.write(music.content)   # .content就是以流的形式写入
        with open(picture_file, 'wb') as f:
            f.write(picture.content)

        music_msg = {
            'music': f'{filename}.mp3',
            'picture': f'{filename}.jpg',
            'title': music_info.get('trackName'),
            'album': music_info.get('albumName'),
            'sort': tar
        }
        music_list.append(music_msg)
        # time.sleep(0.1)
    MONGODB.content.insert_many(music_list)


data_collect('抖音神曲')
