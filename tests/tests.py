import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from zohar_preprocess_file import *
from zohar_split_heuristic import *
from web.models import process, split_content, TranslationModel
import torch
import numpy as np
from time import time
from tqdm import trange


class Args:
    def __init__(self, args):
        for k, v in args.items():
            self.__setattr__(k, v)


def test_send_text(mname='he_en_zohar_V1'):
    with open('multiline.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    args = Args({'bs': 24, 'backend': 'huggingface', 'threads': -1})
    model = TranslationModel(mname, None, args, False, '../web/models/')
    res = model('text', content)
    assert len(res['target'].split('\n')) == 5
    assert len(res['target']) > 100


def test_upload_docx(mname='he_en_zohar_V1'):
    with open('dad.docx', 'rb') as f:
        content = f.read()
    args = Args({'bs': 24, 'backend': 'huggingface', 'threads': -1})
    model = TranslationModel(mname, None, args, False, '../web/models/')
    res = model('application/vnd.openxmlformats-officedocument.wordprocessingml.document', content)
    assert len(res['target'].split('\n')) == 17
    assert len(res['target']) > 1000
