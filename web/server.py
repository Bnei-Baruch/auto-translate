from flask import Flask, current_app, request, jsonify, make_response
import psutil
import os
from models import *
import argparse
import logging

log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# log.disabled = True
# app.logger.disabled = True

@app.route('/', methods=['GET'])
def index():
    return current_app.send_static_file('index.html')


@app.route('/upload', methods=['PUT'])
def upload_translate():
    timestamp = request.args.get('timestamp')
    model_name = request.args.get('model')
    model = TranslationModel(model_name, timestamp, ARGS)
    return model(request.mimetype, request.get_data())


@app.route('/cpu', methods=['GET'])
def get_cpu():
    return {'cpu': int(psutil.cpu_percent())}


@app.route('/progress', methods=['GET'])
def progress():
    timestamp = request.args.get('timestamp')
    with open(f'progress/{timestamp}.txt', 'r') as f:
        txt = f.read()
        curr, total = txt.split('/')
        curr, total = int(curr), int(total)
        prog = 0
        if curr != 0 or total != 0:
            prog = curr / total
    return {'progress': int(100 * prog)}


@app.route('/text', methods=['POST'])
def text_translate():
    timestamp = request.args.get('timestamp')
    model_name = request.args.get('model')
    model = TranslationModel(model_name, timestamp, ARGS)
    content_type = request.mimetype
    text = request.get_data()
    res = model("text", text)
    return {'sourceText': text, 'translatedText': res}


@app.route('/save-as-table', methods=['POST'])
def save_table(timestamp, model):
    pass


@app.route('/translate-models', methods=['GET'])
def model_list():
    return {'models': os.listdir('models')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', default=5000)
    parser.add_argument('--bs', default=1, type=int)
    parser.add_argument('--threads', default=-1, type=int)
    parser.add_argument('--backend', default='huggingface')
    args = parser.parse_args()
    ARGS = args
    shutil.rmtree('progress', ignore_errors=True)
    os.mkdir('progress')
    app.run(host=args.host, port=args.port)
