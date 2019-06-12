import os
import time
from uuid import uuid4

from bson import ObjectId
from flask import Blueprint, request, jsonify
from settings import MONGODB, RET, VOICE_PATH
from baidu_ai import text2audio, audio2text, my_nlp_lowB
from get_set_redis import *

voice = Blueprint('voice', __name__)


@voice.route('/upload/voice', methods=['POST'])
def upload_voice():
    # voice_msg = request.form.to_dict()
    # print(voice_msg)  # task.addData 数据

    from_user = request.form.get('from_user')  # app持有者
    to_user = request.form.get('to_user')  # 玩具
    file = request.files.get('reco')
    filename = file.filename
    filepath = os.path.join(VOICE_PATH, filename)
    file.save(filepath)
    # 转格式
    os.system(f'ffmpeg -i {filepath} {filepath}.mp3')

    # 消息记录存储:
    chat = {
        'from_user': from_user,
        'to_user': to_user,
        'chat': f'{filename}.mp3',
        'create_time': time.time()
    }
    MONGODB.chats.update_one({'user_list': {'$all': [to_user, from_user]}}, {'$push': {'chat_list': chat}})

    # 设置玩具未读消息
    set_redis(to_user, from_user)

    # 消息提醒逻辑
    # 1. 先查询收件人的信息
    toy_info = MONGODB.toys.find_one({'_id': ObjectId(to_user)})
    # 2. 查找收件人通讯录中发件人的昵称或者备注
    user_name = '未知联系人'
    for i in toy_info.get('friend_list'):
        if i.get('friend_id') == from_user:
            user_name = i.get('friend_remark')
    msgNotice = text2audio(f'你有来自亲爱的{user_name}的消息')
    return jsonify({'to_user': to_user, 'from_user': from_user, 'chat': msgNotice})


@voice.route('/upload/toy', methods=['POST'])
def upload_toy():
    reco_file = request.files.get('reco')
    filename = f'{uuid4()}.wav'   # 此处把.wav改成了.mp3
    file_path = os.path.join(VOICE_PATH, filename)
    reco_file.save(file_path)

    from_user = request.form.get('from_user')  # 这个是toy_id
    to_user = request.form.get('to_user')  # 这个是APP

    chat = {
        'from_user': from_user,
        'to_user': to_user,
        'chat': filename,
        'create_time': time.time()
    }
    MONGODB.chats.update_one({'user_list': {'$all': [to_user, from_user]}}, {'$push': {'chat_list': chat}})

    toy_info = MONGODB.toys.find_one({'_id': ObjectId(to_user)})
    # 2. 查找收件人通讯录中发件人的昵称或者备注
    if toy_info:
        user_name = '未知联系人'
        for i in toy_info.get('friend_list'):
            print(i.get('from_user'))
            print(from_user)
            if i.get('friend_id') == from_user:
                user_name = i.get('friend_remark')

        filename = text2audio(f'你有来自亲爱的{user_name}的消息')

    # 设置玩具未读消息
    set_redis(to_user, from_user)

    return jsonify({'to_user': to_user, 'from_user': from_user, 'chat': filename})


@voice.route('/upload/ai', methods=['POST'])
def upload_ai():
    reco_file = request.files.get('reco')
    toy_id = request.form.get('toy_id')
    filename = f'{uuid4()}.wav'
    file_path = os.path.join(VOICE_PATH, filename)
    reco_file.save(file_path)
    text = audio2text(file_path)
    ret = my_nlp_lowB(text, toy_id)
    return jsonify(ret)  # {'from_user': friend.get('friend_id'), 'chat': filename}


@voice.route('/recv/msg', methods=['POST'])
def recv_msg():
    from_user = request.form.get('from_user')
    to_user = request.form.get('to_user')

    from_user, count = get_redis(to_user, from_user)
    chat_info = MONGODB.chats.find_one({'user_list': {'$all': [from_user, to_user]}})

    # 发送所有未读的消息
    # msg = chat_info.get('chat_list')[-count:]  # type:list

    # reversed是匿名函数,有返回值,reverse是list中的方法,没有返回值
    msg_list = reversed(chat_info.get('chat_list'))
    new_msg_list = []
    for msg in msg_list:
        if msg.get('from_user') != to_user:
            new_msg_list.append(msg)
        if len(new_msg_list) >= count:
            break

    toy_info = MONGODB.toys.find_one({'_id': ObjectId(to_user)})
    user_name = '未知联系人'
    for i in toy_info.get('friend_list'):
        if i.get('friend_id') == from_user:
            user_name = i.get('friend_remark')
    msgNotice = text2audio(f'以下是来自{user_name}的消息')

    new_msg_list.append({'from_user': from_user, 'chat': msgNotice})

    return jsonify(new_msg_list)


@voice.route('/chat/list', methods=['POST'])
def chat_list():
    chat_id = request.form.get('chat_id')
    to_user = request.form.get('to_user')
    from_user = request.form.get('from_user')
    chat_list = MONGODB.chats.find_one({'_id': ObjectId(chat_id)}).get('chat_list')
    chat_num = chat_list[-5:]
    # print('聊天列表', chat_list)
    RET['code'] = 0
    RET['msg'] = '查询消息列表'
    RET['data'] = chat_num

    get_redis(to_user, from_user)
    return jsonify(RET)


@voice.route('/unread/msg', methods=['POST'])
def unread_msg():
    to_user = request.form.get('to_user')  # APP
    chat_info = get_redis_all(to_user)
    RET['code'] = 0
    RET['msg'] = '未读消息'
    RET['data'] = chat_info
    return jsonify(RET)


@voice.route('/personal/unread/msg', methods=['POST'])
def personal_unread_msg():
    from_user = request.form.get('toy_id')  # toy_id
    to_user = request.form.get('app_id')  # app_id
    count = get_redis(to_user, from_user)
    RET['code'] = 0
    RET['msg'] = '未读消息'
    RET['data'] = str(count)
    # print('有没有值啊',RET)
    return jsonify(RET)
