from bson import ObjectId
from flask import Blueprint, request, jsonify
from settings import MONGODB, RET

devices = Blueprint('devices', __name__)


@devices.route('/verify_device_key', methods=['POST'])
def verify_device_key():
    device_info = request.form.to_dict()
    # mongodb的筛选方法, {字段:0}   后面定要是0 表示不要这个字段
    device = MONGODB.devices.find_one(device_info, {'_id': 0})
    if device:
        # 是授权设备
        toy_info = MONGODB.toys.find_one(device_info)
        if toy_info:
            toy_info['_id'] = str(toy_info.get('_id'))
            RET['code'] = 1  # 添加好友逻辑
            RET['msg'] = '玩具已经存在,开启添加好友'
            RET['data'] = toy_info
        else:
            RET['code'] = 0
            RET['msg'] = '扫码成功'
            RET['data'] = device
    else:
        # 不是授权设备
        RET['code'] = -1
        RET['msg'] = '这不是玩具的二维码'

    return jsonify(RET)  # 返回device_key


@devices.route('/bind/toy', methods=['POST'])
def bind_toy():
    toy_info = request.form.to_dict()  # {toy_name,baby_name,remark,device_key,user_id}
    # 自己添加
    toy_info['bind_user'] = toy_info.pop('user_id')   # 把user_id换成bind_id
    # 查询用户的数据
    app_user = MONGODB.users.find_one({'_id': ObjectId(toy_info['bind_user'])})
    # 创建聊天窗口,双方是谁,还有聊了什么
    chat_window = MONGODB.chats.insert_one({'user_list': [], 'chat_list': []})
    # 应该是活的上传的,放到avatar目录里,有时间写
    toy_info['avatar'] = 'toy.jpg'
    # toy_info['friend_list'] = []
    # 绑定好友版
    toy_info['friend_list'] = [{
        'friend_id': toy_info['bind_user'],
        'friend_nick': app_user.get('nickname'),
        'friend_avatar': app_user.get('avatar'),
        'friend_remark': toy_info.pop('remark'),
        'friend_type': 'app',  # 区分当前好友是玩具还是app
        'friend_chat': str(chat_window.inserted_id)
    }]
    toy = MONGODB.toys.insert_one(toy_info)
    app_add_toy = {
        'friend_id': str(toy.inserted_id),
        'friend_nick': toy_info.get('toy_name'),
        'friend_avatar': toy_info.get('avatar'),
        'friend_remark': toy_info.get('baby_name'),
        'friend_type': 'toy',  # 区分当前好友是toy还是app
        'friend_chat': str(chat_window.inserted_id)
    }
    app_user['friend_list'].append(app_add_toy)
    app_user['bind_toy'].append(str(toy.inserted_id))
    # user数据全部更新
    MONGODB.users.update_one({'_id': ObjectId(toy_info['bind_user'])}, {'$set': app_user})
    # 把单聊的俩个人的id放到user_list里面
    user_list = [toy_info['bind_user'], str(toy.inserted_id)]
    # 更新当前的聊天窗口数据
    MONGODB.chats.update_one({'_id': chat_window.inserted_id}, {'$set': {'user_list': user_list}})

    # MONGODB.users.update_one({'_id': ObjectId(toy_info['bind_user'])},
    #                          {'$push': {'bind_toy': str(toy.inserted_id)}})
    RET['code'] = 0
    RET['msg'] = '绑定成功'
    return jsonify(RET)


@devices.route('/bind/toy/list', methods=['POST'])
def bind_toy_list():
    user_id = request.form.get('user_id')
    # 要转成列表
    toy_list = list(MONGODB.toys.find({'bind_user': user_id}))

    for index, toy in enumerate(toy_list):
        # 如果不是列表不能进行这部操作
        toy_list[index]['_id'] = str(toy.get('_id'))

    RET['code'] = 0
    RET['msg'] = '查询绑定玩具列表'
    RET['data'] = toy_list
    return jsonify(RET)  # 玩具信息和玩具朋友信息


@devices.route('/toy/open', methods=['POST'])
def toy_open():
    device_key = request.form.to_dict()  # {device_key:9827982398}
    toy_info = MONGODB.toys.find_one(device_key)
    if toy_info:  # 开机成功
        return jsonify(
            {'music': 'success.mp3', 'toy_id': str(toy_info.get('_id')), 'toy_name': toy_info.get('toy_name')})
    else:
        device = MONGODB.devices.find_one(device_key)
        if device:  # 没有绑定
            return jsonify({'music': 'noBind.mp3'})
        else:  # 根本没有授权
            return jsonify({'music': 'noLicense.mp3'})


# 测试播放录音
@devices.route('/voice/open', methods=['POST'])
def voice_open():
    device_key = request.form.to_dict()  # {device_key:9827982398}
    toy_info = MONGODB.toys.find_one(device_key)
    if toy_info:  # 开机成功
        return jsonify(
            {'music': 'success.mp3', 'toy_id': str(toy_info.get('_id')), 'toy_name': toy_info.get('toy_name')})
