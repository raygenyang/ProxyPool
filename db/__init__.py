import redis
import settings
import json
import time


def dec(func):
    def wrapper(*args):
        s_time = time.time()
        ret = func(*args)
        e_time = time.time()
        print(e_time - s_time)
        return ret
    return wrapper


# 基于Redis的有序集合实现的带去重功能的优先级队列(数值大的优先)
class RedisQueue(object):
    def __init__(self, name, url=None, host=None, port=None, passwd=None, db=0):
        self.name = name
        self.host = host or getattr(settings, 'REDIS_HOST', '127.0.0.1')
        self.port = port or int(getattr(settings, 'REDIS_PORT', 6379))
        self.passwd = passwd or getattr(settings, 'REDIS_PASSWD', None)
        self.db = db or int(getattr(settings, 'REDIS_DB', 0))
        self._pop_lua = None
        self._conn = redis.StrictRedis(self.host, self.port, self.db, self.passwd)

    # 返回元素但不删除
    @dec
    def get(self, num=1):
        values = self._conn.zrevrange(self.name, 0, num-1)
        # values = self._conn.eval('return redis.call("zrevrange", KEYS[1], 0, ARGV[1])', 1, self.name, num-1)
        rst = []
        for value in values:
            temp = value.decode()
            try:
                temp = json.loads(temp)
            except json.JSONDecodeError:
                pass
            rst.append(temp)
        return rst

    # 加入队列
    @dec
    def put(self, *args):
        pieces = []
        for arg in args:
            if not isinstance(arg, tuple) or len(arg) != 2:
                raise redis.RedisError('arg must be a tuple with two members')
            if isinstance(arg[0], (list, tuple, dict)):
                p = json.dumps(arg[0])
            else:
                p = arg[0]
            pieces.extend((arg[1], p))
        return self._conn.execute_command('ZADD', self.name, *pieces)

    # 返回元素并删除
    @dec
    def pop(self, num=1):
        if self._pop_lua is None:
            self._pop_lua = """
                local values = redis.call("zrevrange", KEYS[1], 0, ARGV[1])
                redis.call("zremrangebyrank", KEYS[1], -ARGV[1]-1, -1)
                return values
            """
            self._pop_lua = self._conn.script_load(self._pop_lua)
        values = self._conn.evalsha(self._pop_lua, 1, self.name, num-1)
        rst = []
        for value in values:
            temp = value.decode()
            try:
                temp = json.loads(temp)
            except json.JSONDecodeError:
                pass
            rst.append(temp)
        return rst

    @dec
    def qsize(self, min='-inf', max='+inf'):
        return self._conn.zcount(self.name, min=min, max=max)


