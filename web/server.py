from flask import Flask, current_app, request
from models import ACTIVE
import argparse

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return current_app.send_static_file('index.html')


@app.route('/', methods=['PUT'])
def upload():
    return model(request.mimetype, request.get_data())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=5000)
    parser.add_argument('--bs', default=1, type=int)
    parser.add_argument('--threads', default=1, type=int)
    args = parser.parse_args()
    model = ACTIVE(args)

    app.run(host=args.host, port=args.port)
