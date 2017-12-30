import redis
import settings
import json
import sys
import random

class RedisDB(object):
    def __init__(self, name, host=None, port=None, passwd=None, db=0):
        self.name = name
        self.host = host or getattr(settings, 'REDIS_HOST', '127.0.0.1')
        self.port = port or int(getattr(settings, 'REDIS_PORT', 6379))
        self.passwd = passwd or getattr(settings, 'REDIS_PASSWD', None)
        self.db = db or int(getattr(settings, 'REDIS_DB', 0))
        self._conn = redis.Redis(self.host, self.port, self.db, self.passwd)

    def get(self):
        """
        get random result
        :return:
        """
        key = self._conn.hgetall(name=self.name)
        # return random.choice(key.keys()) if key else None
        # key.keys()在python3中返回dict_keys，不支持index，不能直接使用random.choice
        # 另：python3中，redis返回为bytes,需要解码
        rkey = random.choice(list(key.keys())) if key else None
        if isinstance(rkey, bytes):
            return rkey.decode('utf-8')
        else:
            return rkey
            # return self.__conn.srandmember(name=self.name)

    def put(self, key):
        """
        put an  item
        :param value:
        :return:
        """
        key = json.dumps(key) if isinstance(key, (dict, list)) else key
        return self._conn.hincrby(self.name, key, 1)
        # return self.__conn.sadd(self.name, value)

    def getvalue(self, key):
        value = self._conn.hget(self.name, key)
        return value if value else None

    def pop(self):
        """
        pop an item
        :return:
        """
        key = self.get()
        if key:
            self._conn.hdel(self.name, key)
        return key
        # return self.__conn.spop(self.name)

    def delete(self, key):
        """
        delete an item
        :param key:
        :return:
        """
        self._conn.hdel(self.name, key)
        # self.__conn.srem(self.name, value)

    def inckey(self, key, value):
        self._conn.hincrby(self.name, key, value)

    def getAll(self):
        # return self.__conn.hgetall(self.name).keys()
        # python3 redis返回bytes类型,需要解码
        if sys.version_info.major == 3:
            return [key.decode('utf-8') for key in self._conn.hgetall(self.name).keys()]
        else:
            return self._conn.hgetall(self.name).keys()
            # return self.__conn.smembers(self.name)

    def get_status(self):
        return self._conn.hlen(self.name)
        # return self.__conn.scard(self.name)

    def changeTable(self, name):
        self.name = name