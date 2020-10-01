from flask import Flask, current_app, request
from models import ACTIVE
import argparse

app = Flask(__name__)
model = ACTIVE()

@app.route('/', methods=['GET'])
def index():
    return current_app.send_static_file('index.html')

@app.route('/', methods=['PUT'])
def upload():
    return model(request.get_data())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', default=5000)
    args = parser.parse_args()

    app.run(host=args.host, port=args.port)
