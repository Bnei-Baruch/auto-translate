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


def timed_test(mname):
    with open('dad.docx', 'rb') as f:
        content = f.read()
    for bs in [24]:
        print(bs)
        start = time()
        args = Args({'bs': bs, 'backend': 'huggingface', 'threads': -1})
        model = TranslationModel(mname, None, args, False, '../web/models/')
        translate_start = time()
        res = model('application/vnd.openxmlformats-officedocument.wordprocessingml.document', content)
        print(res)
        with open('results.txt', 'w') as f:
            f.write(res['target'])
        end = time()
        print('Total time: ', end - start)
        print('Translation time: ', end - translate_start)


if __name__ == '__main__':
    timed_test('he_en_zohar_V2')
