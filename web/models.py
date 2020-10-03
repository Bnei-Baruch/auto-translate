from zohar_preprocess_file import *
from zohar_split_heuristic import *
import os
import gdown
from zipfile import ZipFile
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import numpy as np
import shutil
from time import time


def process(content, lang='he'):
    "the main logic: splits the input into chunks, runs replacement regexes and saves the output"
    output = paragraphs(content)
    output = replace(output, lang)
    return output


def split_content(content, max_words, source):
    res = split_letters_source(content, max_words=max_words, source=source)
    output, letters_processed, letters_total = res
    print(f'Processed {letters_processed} letters out of {letters_total} ({100*letters_processed/letters_total}%)')
    return output

class Model1:
    def __call__(self, mimetype, text):
        if mimetype.startswith("text"):
            return {'en': 'Translation 1', 'he': text.decode()}
        return {'en': 'Translation 1', 'he': 'המקור אינו קובץ טקסט'}


class Model2:
    def __call__(self, mimetype, text):
        return {'en': 'Translation 2', 'he': 'מקור'}


class BadModel:
    def __call__(self, text):
        raise Exception('Failed')


class TranslationModel:
    def __init__(self, bs):
        self.bs = bs
        if not os.path.exists('model'):
            url = 'https://drive.google.com/u/0/uc?id=1JxFMdUAKGjEuGZAMdHnGrMvJrf9YVi-I&export=download'
            output = 'model.zip'
            gdown.download(url, output, quiet=False)
            with ZipFile('model.zip', 'r') as zipf:
                zipf.extractall()
            shutil.move('content/model', 'model')
            shutil.rmtree('content')
        mname = 'model'
        self.torch_device = 'cpu'
        self.trained_model = AutoModelForSeq2SeqLM.from_pretrained(mname).to(self.torch_device)
        self.trained_tok = AutoTokenizer.from_pretrained(mname)

    def translate(self, s):
        bs = self.bs
        t = time()
        res_arr = []
        batch_s = s.split('\n')
        if bs != -1:
            n_batches = int(np.ceil(len(batch_s) / bs))
            for b in range(n_batches):
                start = b*bs
                end = start+bs
                curr_batch = batch_s[start:end]
                trained_batch = self.trained_tok(curr_batch, return_tensors='pt', padding=True).to(self.torch_device)
                trained_translated = self.trained_model.generate(**trained_batch, num_beams=5, early_stopping=True)
                trained_translated_txt = self.trained_tok.batch_decode(trained_translated, skip_special_tokens=True)
                res_arr.extend(trained_translated_txt)
        else:
            trained_batch = self.trained_tok(batch_s, return_tensors='pt', padding=True).to(self.torch_device)
            trained_translated = self.trained_model.generate(**trained_batch, num_beams=5, early_stopping=True)
            trained_translated_txt = self.trained_tok.batch_decode(trained_translated, skip_special_tokens=True)
            res_arr = trained_translated_txt
        result = '\n'.join(res for res in res_arr)
        print(f'Time taken: {time() - t}, batch size: {bs}')
        return result

    def __call__(self, mimetype, content):
        if mimetype.startswith("text"):
            txt = content.decode()
            return {'en': self.translate(txt), 'he': txt}
        elif mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            processed_content = process(content)
            split_txt = split_content(processed_content, max_words=300, source='he')
            txt = join_text(split_txt)
            return {'en': self.translate(txt), 'he': txt}
        return {'en': 'Translation 1', 'he': 'המקור אינו קובץ טקסט'}


ACTIVE = TranslationModel
