import os
import gdown
from zipfile import ZipFile
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import shutil


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
    def __init__(self):
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
        trained_batch = self.trained_tok(s, return_tensors='pt').to(self.torch_device)  # , padding=True
        trained_translated = self.trained_model.generate(**trained_batch, num_beams=5, early_stopping=True)
        trained_translated_txt = self.trained_tok.batch_decode(trained_translated, skip_special_tokens=True)
        return trained_translated_txt[0]

    def __call__(self, mimetype, text):
        if mimetype.startswith("text"):
            txt = text.decode()
            return {'en': self.translate(txt), 'he': txt}
        return {'en': 'Translation 1', 'he': 'המקור אינו קובץ טקסט'}


ACTIVE = Model1
