from flask import Blueprint, jsonify
from settings import MONGODB, RET

content = Blueprint('content', __name__)


@content.route('/content/list', methods=['POST'])
def content_list():
    # 这是个生成器,需要list拿数据
    res = list(MONGODB.content.find())
    # print(res)
    if res:
        for index, cont in enumerate(res):
            res[index]['_id'] = str(cont.get('_id'))
        RET['code'] = 0
        RET['msg'] = '查询内容列表'
        RET['data'] = res
        # print(RET)
    else:
        RET['code'] = -1
        RET['msg'] = '没有数据'

    return jsonify(RET)
