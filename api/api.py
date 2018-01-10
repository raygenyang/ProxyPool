from flask import Flask, request
from db import RedisQueue
import json
import pickle

app = Flask(__name__)
queue = RedisQueue('ProxyPool')


@app.route('/get', methods=['GET', 'POST'])
def get():
    r = request
    print(request.headers)
    return json.dumps(queue.get(5))


@app.route('/pop', methods=['GET', 'POST'])
def pop():
    return json.dumps(queue.pop(5))


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)

