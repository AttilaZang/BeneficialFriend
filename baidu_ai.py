import os
from content_sim import my_sim
import requests
from bson import ObjectId
from pypinyin import lazy_pinyin, TONE2
from settings import SPEECH_CLIENT, VOICE_PATH, VOICE, MONGODB, TULING_URL, TULING_DATA
from uuid import uuid4


def text2audio(text):
    filename = f'{uuid4()}.mp3'
    file_path = os.path.join(VOICE_PATH, filename)
    result = SPEECH_CLIENT.synthesis(text, 'zh', 1, VOICE)
    if not isinstance(result, dict):
        with open(file_path, 'wb') as f:
            f.write(result)
    return filename


def get_file_content(filePath):
    # 这个是固定写法,用ffmpeg把别的格式的音频转化为.pcm格式的
    os.system(f'ffmpeg -y  -i {filePath}  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {filePath}.pcm')
    with open(f'{filePath}.pcm', 'rb') as fp:
        return fp.read()


def audio2text(filePath):
    # 识别本地文件,hot.m4a是放在本地的音频文件,下面的参数ai.baidu.com有详解
    reg = SPEECH_CLIENT.asr(get_file_content(filePath), 'pcm', 16000, {
        'dev_pid': 1536,
    })
    print(reg['result'][0])
    return reg['result'][0]


def to_tuling(text, toy_id):
    TULING_DATA['perception']['inputText']['text'] = text
    TULING_DATA['userInfo']['userId'] = toy_id
    # 请求方式必须是HTTP POST, 参数格式必须是json
    ret = requests.post(TULING_URL, json=TULING_DATA)
    # print(ret.json())
    return ret.json().get('results')[0].get('values').get('text')


# 自然语言处理
def my_nlp_lowB(text, toy_id):
    print('自然语言处理', toy_id)
    if '发消息' in text:
        text_py = ''.join(lazy_pinyin(text, style=TONE2))
        toy_info = MONGODB.toys.find_one({'_id': ObjectId(toy_id)})
        for friend in toy_info.get('friend_list'):
            print('别名是啥',friend.get('friend_nick'),friend.get('remark_py'))
            nick_py = ''.join(lazy_pinyin(friend.get('friend_nick'), style=TONE2))
            remark_py = ''.join(lazy_pinyin(friend.get('friend_remark'), style=TONE2))
            if nick_py in text or remark_py in text_py:
                filename = text2audio(f'可以给{friend.get("friend_remark")}发消息了')
                return {'from_user': friend.get('friend_id'), 'chat': filename}

    if '播放' in text or '来一首' in text or '我想听' in text or '放一首' in text:
        content = my_sim(text)
        return {'from_user': 'ai', 'music': content.get('music')}
        # content_list = MONGODB.content.find({})
        # for content in content_list:
        #     if content.get('title') in text:
        #         return {'from_user': 'ai', 'music': content.get('music')}

    new_text = to_tuling(text, toy_id)
    new_filename = text2audio(new_text)
    return {'from_user': 'ai', 'chat': new_filename}


if __name__ == '__main__':
    print(text2audio('消息已成功发送'))  # 需要拿文件名
