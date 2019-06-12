from bson import ObjectId
from flask import Blueprint, request, jsonify
from settings import MONGODB, RET

user = Blueprint('login', __name__)


@user.route('/register', methods=['POST'])
def register():
    user_info = request.form.to_dict()
    # print(user_info)
    user_info['avatar'] = 'boy.jpg' if user_info.get('gender') == '1' else 'girl.jpg'
    user_info['friend_list'] = []
    user_info['bind_toy'] = []

    MONGODB.users.insert_one(user_info)

    RET['code'] = 0
    RET['msg'] = '注册成功'
    return jsonify(RET)


@user.route('/login', methods=['POST'])
def login():
    user = request.form.to_dict()
    user_info = MONGODB.users.find_one(user)
    user_info['_id'] = str(user_info.get('_id'))
    user_info['bind_toy'] = str(user_info.get('bind_toy'))
    print('>>>>>', user_info)
    RET['code'] = 0
    RET['msg'] = '登录成功'
    RET['data'] = user_info
    return jsonify(RET)


@user.route('/auto_login', methods=['POST', 'GET'])
def auto_login():
    user_id = request.form.get('_id')
    user_info = MONGODB.users.find_one({'_id': ObjectId(user_id)})

    user_info['_id'] = str(user_info.get('_id'))
    print('>>>>>>>', user_info)
    RET['code'] = 0
    RET['msg'] = '登录成功'
    RET['data'] = user_info
    return jsonify(RET)
