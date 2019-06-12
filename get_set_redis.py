import json

from settings import REDIS_DB


#  存储未读消息
def set_redis(to_user, from_user):
    # 如果app给玩具发消息,那么站在app的角度上to_user就是玩具,from_user就是app
    # 这里的to_user也是玩具,所以get(to_user)就是get自己
    self_redis = REDIS_DB.get(to_user)  # 查看数据库中是否存在自己的空间,如果有就+1,没有就创建
    if self_redis:
        chat_dict = json.loads(self_redis)  # 先到redis中loads,看看有没有数据
        chat_dict.setdefault(from_user, 0)
        chat_dict[from_user] += 1
        REDIS_DB.set(to_user, json.dumps(chat_dict))

    else:
        # {'我':{'联系人1号':1,'联系人2号':3}}  redis中没有字典类型,需要哈希存储能拿字典
        # 所以我们可以换思路,把字典给json,变成字符串
        chat = {from_user: 1}  # 因为一次只能发一条消息,所以默认为1
        REDIS_DB.set(to_user, json.dumps(chat))


# 读取未读消息
def get_redis(to_user, from_user):
    # 如果app给玩具发消息,那么站在app的角度上to_user就是玩具,from _user就是app
    # 这里的to_user也是玩具,所以get(to_user)就是get自己
    self_redis = REDIS_DB.get(to_user)
    count = 0
    if self_redis:
        chat_dict = json.loads(self_redis)  # 先到redis中loads,看看有没有数据
        chat_dict.setdefault(from_user, 0)
        count = chat_dict[from_user]

        if count == 0:
            key, value = re_get_redis(chat_dict)
            if key:
                from_user = key
                count = value

        chat_dict[from_user] = 0
        REDIS_DB.set(to_user, json.dumps(chat_dict))
    return from_user, count


# 重新收取一次不为0的未读消息
def re_get_redis(to_user_info):
    for from_user, count in to_user_info.items():
        if count != 0:
            return from_user, count
    return 0, 0


# 获取全局未读
def get_redis_all(to_user):
    self_redis = REDIS_DB.get(to_user)

    chat_dict = {'count': 0}
    if self_redis:
        chat_dict = json.loads(self_redis)  # {'联系人1号':1,'联系人2号':3}
        # 添加一个未读数据的总和
        chat_dict['count'] = sum(chat_dict.values())
    return chat_dict
