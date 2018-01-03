from flask import Flask
from db.queue import RedisQueue
import json

app = Flask(__name__)
queue = RedisQueue('ProxyPool')


@app.route('/get', methods=['GET', 'POST'])
def get():
    return json.dumps(queue.get())


if __name__ == '__main__':
    app.run()

