import os
import redis
import pickle
import re

try:
    if os.environ["REDIS_HOST"]:
        try:
            redis_client = redis.Redis(host=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"], db=0)
        except KeyError:
            redis_client = redis.Redis(host=os.environ["REDIS_HOST"])
except KeyError:
    os.environ["REDIS_HOST"] = ''


def check_token(auth_token):
    if not os.environ["REDIS_HOST"]:
        print('not redis host')
        return True

    if auth_token is not None:
        auth_token = str(auth_token)
        token = auth_token.replace('Bearer ', '')
        token = redis_client.get(token)
        print("TOKEN", token)
        if token is None:
            return True
        else:
            redis_client.setex(token, 60*60, token)
            return False
    else:
        return True


def redis_set(key: str, value: str):
    if not os.environ["REDIS_HOST"]:
        return {}
    redis_client.set(key, value)


def redis_tem_set(key: str, time: int, value: str):
    if not os.environ["REDIS_HOST"]:
        return {}
    redis_client.setex(key, time, value)


def redis_get(key: str):
    if not os.environ["REDIS_HOST"]:
        return {}
    return redis_client.get(key)


def redis_hset(key: str, data: dict):
    if not os.environ["REDIS_HOST"]:
        return {}
    redis_client.hmset(key, data)


def redis_temp_hset(key: str, data: dict, expire: int = None):
    if not os.environ["REDIS_HOST"]:
        return {}
    redis_client.hmset(key, data)
    if expire:
        redis_client.expire(key, expire)


def redis_hgetall(key: str):
    if not os.environ["REDIS_HOST"]:
        return {}
    y = {}
    r = redis_client.hgetall(key)

    for keyy, value in r.items():
        try:
            if re.match(r'^-?\d+(?:\.\d+)$', value.decode("utf-8")) is None:
                y[keyy.decode("utf-8")] = int(value.decode("utf-8"))
            else:
                y[keyy.decode("utf-8")] = float(value.decode("utf-8"))
        except ValueError:
            y[keyy.decode("utf-8")] = value.decode("utf-8")
    return y


def redis_set_json(key, data, ex=0):
    if not os.environ["REDIS_HOST"]:
        return {}
    if ex > 0:
        redis_client.set(key, pickle.dumps(data), ex=ex)
    else:
        redis_client.set(key, pickle.dumps(data))


def redis_get_json(key):
    if not os.environ["REDIS_HOST"]:
        return {}
    data = redis_client.get(key)
    if data:
        try:
            return pickle.loads(data)
        except:
            return eval(data.decode())
    return {}

