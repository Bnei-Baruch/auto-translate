from flask import Flask, current_app, request, jsonify, make_response
import psutil
from tabulate import tabulate
import os
from models import *
import argparse
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

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
    text = request.get_data().decode()
    if content_type.endswith('json'):
        text = request.json['text']
    res = model("text", text)
    return res


@app.route('/save-as-table', methods=['POST'])
def save_table():
    langs = {'he': 'Hebrew', 'en': 'English', 'sp': 'Spanish'}
    model_name = request.args.get('model')
    source, target = model_name.split('_')[0], model_name.split('_')[1]
    alignment = 'standard'
    if 'he' == source or 'he' == target:
        alignment = 'special'
    inp = request.json['textInput'].replace('\n\n', '\n')
    outp = request.json['textOutput'].replace('\n\n', '\n')
    order = tuple()
    if alignment == 'special' and 'he' == source:
        order = zip(outp.split('\n'), inp.split('\n'))
    else:
        order = zip(inp.split('\n'), outp.split('\n'))
    raw_table = [list(t) for t in order]
    headers = []
    if alignment == 'special' and 'he' == source:
        headers = [langs[target], langs[source]]
    else:
        headers = [langs[source], langs[target]]
    colalign = ('left', 'right' if alignment == 'special' else 'left')
    table = tabulate(raw_table, tablefmt='html', headers=headers, colalign=colalign)
    return {'table': table}


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
