from bson import ObjectId
from flask import Blueprint, request, jsonify
from settings import MONGODB, RET

friend = Blueprint('friend', __name__)


@friend.route('/friend/list', methods=['POST'])
def friend_list():
    user_id = request.form.get('_id')
    user_info = MONGODB.users.find_one({'_id': ObjectId(user_id)})
    RET['code'] = 0
    RET['msg'] = '好友列表查询'
    RET['data'] = user_info.get('friend_list')
    print('========', RET)
    return jsonify(RET)  # 玩具列表


@friend.route('/add/req', methods=['POST'])
def add_req():
    req_info = request.form.to_dict()
    # print('怎么能没有东西===>', req_info)
    if req_info.get('type') == 'toy':
        user_info = MONGODB.toys.find_one({'_id': ObjectId(req_info.get('toy_id'))})   # 申请人的信息
    else:
        user_info = MONGODB.users.find_one({'_id': ObjectId(req_info.get('toy_id'))})

    req_info['user_avatar'] = user_info.get('avatar')
    req_info['req_info'] = req_info.get('user_name') + ':' + req_info['req_info']

    req_info['status'] = 0

    MONGODB.request.insert_one(req_info)

    RET['code'] = 0
    RET['msg'] = '添加好友请求'
    RET['data'] = {}

    return jsonify(RET)


@friend.route('/acc/req', methods=['POST'])
def acc_req():
    req_id = request.form.get('req_id')  # 申请人id
    req_info = MONGODB.request.find_one({'_id': ObjectId(req_id)})
    remark = request.form.get('remark')
    # print('真的没有备注么======>', remark)
    if req_info.get('type') == 'toy':
        user_info = MONGODB.toys.find_one({'_id': ObjectId(req_info.get('user_id'))})  # 被申请人info
    else:
        user_info = MONGODB.users.find_one({'_id': ObjectId(req_info.get('user_id'))})
        # req_info.get('user_id')) 拿到你要添加那个玩具的信息
    toy_info = MONGODB.toys.find_one({'_id': ObjectId(req_info.get('toy_id'))})  # 申请人info
    chat_window = MONGODB.chats.insert_one(
        {'user_list': [req_info.get('user_id'), req_info.get('toy_id')], 'chat_list': []})
    user_add_toy = {  # 被申请人同意添加申请人
        'friend_id': str(toy_info.get('_id')),
        'friend_nick': toy_info.get('baby_name'),
        'friend_avatar': toy_info.get('avatar'),
        'friend_remark': remark,
        'friend_type': 'toy',  # 区分当前好友是玩具还是app
        'friend_chat': str(chat_window.inserted_id)
    }
    toy_add_user = {  # 申请人添加被申请人
        'friend_id': str(user_info.get('_id')),
        'friend_nick': user_info.get('baby_name') if req_info.get('type') == 'toy' else user_info.get('nickname'),
        'friend_avatar': user_info.get('avatar'),
        'friend_remark': req_info.get('user_toy_remark'),
        'friend_type': req_info.get('type'),  # 区分当前好友是玩具还是app
        'friend_chat': str(chat_window.inserted_id)
    }

    if req_info.get('type') == 'toy':
        MONGODB.toys.update_one({'_id': ObjectId(req_info.get('user_id'))},
                                {'$push': {'friend_list': user_add_toy}})
    else:
        MONGODB.users.update_one({'_id': ObjectId(req_info.get('user_id'))},
                                 {'$push': {'friend_list': user_add_toy}})

    MONGODB.toys.update_one({'_id': ObjectId(req_info.get('toy_id'))},
                            {'$push': {'friend_list': toy_add_user}})

    MONGODB.request.update_one({'_id': ObjectId(req_id)}, {'$set': {'status': 1}})

    RET['code'] = 0
    RET['msg'] = '同意请求'
    RET['data'] = {}

    return jsonify(RET)


@friend.route('/ref/req', methods=['POST'])
def ref_req():
    req_id = request.form.get('req_id')
    MONGODB.request.update_one({'_id': ObjectId(req_id)}, {'$set': {'status': 2}})

    RET['code'] = 0
    RET['msg'] = '拒绝请求'
    RET['data'] = {}

    return jsonify(RET)


@friend.route('/req/list', methods=['POST'])
def req_list():
    user_id = request.form.get('user_id')
    toy_id_list = MONGODB.users.find_one({'_id': ObjectId(user_id)}).get('bind_toy')

    my_req_list = list(MONGODB.request.find({'toy_id': {'$in': toy_id_list}, 'status': 0}))

    for index, req in enumerate(my_req_list):
        my_req_list[index]['_id'] = str(req.get('_id'))

    RET['code'] = 0
    RET['msg'] = '好友请求列表'
    RET['data'] = my_req_list

    return jsonify(RET)
