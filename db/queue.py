import redis
import settings
import json


class RedisQueue(object):
    def __init__(self, name, url=None, host=None, port=None, passwd=None, db=0):
        self.name = name
        self.host = host or getattr(settings, 'REDIS_HOST', '127.0.0.1')
        self.port = port or int(getattr(settings, 'REDIS_PORT', 6379))
        self.passwd = passwd or getattr(settings, 'REDIS_PASSWD', None)
        self.db = db or int(getattr(settings, 'REDIS_DB', 0))
        self._conn = redis.StrictRedis(self.host, self.port, self.db, self.passwd)

    def get(self, num=1):
        vaules = self._conn.zrevrange(self.name, 0, num-1)
        rst = []
        for value in vaules:
            temp = value.decode()
            try:
                temp = json.loads(temp)
            except json.JSONDecodeError:
                pass
            rst.append(temp)
        return rst

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

    def qsize(self, min='-inf', max='+inf'):
        return self._conn.zcount(self.name, min=min, max=max)

