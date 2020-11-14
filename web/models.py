import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from zohar_preprocess_file import *
from zohar_split_heuristic import *
import gdown
from zipfile import ZipFile
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import numpy as np
import shutil
from time import time
from tqdm import trange
# from fairseq.models.transformer import TransformerModel


def model_setup():
    if not os.path.exists('models/he_en_zohar_V1_nov-14-20'):
        url = 'https://drive.google.com/u/0/uc?id=1pbiJNqtQ3W4fJmk3cH-8sD-mZ7eUp4JK&export=download'  # new
        output = 'model.zip'
        gdown.download(url, output, quiet=False)
        with ZipFile('model.zip', 'r') as zipf:
            zipf.extractall()
        shutil.move('content/model', 'models/he_en_zohar_V1_nov-14-20')
        shutil.rmtree('content')


def process(content, lang='he'):
    "the main logic: splits the input into chunks, runs replacement regexes and saves the output"
    output = paragraphs(content)
    output = replace(output, lang)
    return output


def split_content(content, max_words, source):
    res = split_letters_source(content, max_words=max_words, source=source)
    output, words_processed, words_total = res
    print(f'Processed {words_processed} words out of {words_total} ({100*words_processed/words_total}%)')
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
    def __init__(self, model, timestamp, args):
        self.timestamp = timestamp
        with open(f'progress/{self.timestamp}.txt', 'w') as f:
            f.write('0/0')
        self.bs = args.bs
        self.backend = args.backend
        if args.threads != -1:
            torch.set_num_threads(args.threads)
        print(f'Running with {torch.get_num_threads()} threads.')
        if self.backend == 'huggingface':
            mname = 'models/he_en_zohar_V1_nov-14-20'
            self.torch_device = 'cpu'
            self.trained_model = AutoModelForSeq2SeqLM.from_pretrained(mname).to(self.torch_device)
            self.trained_tok = AutoTokenizer.from_pretrained(mname)

    def get_translated_text(self, text):
        text = [t for t in text if t]
        trained_translated_txt = ['']
        if not text: return trained_translated_txt
        if self.backend == 'huggingface':
            trained_batch = self.trained_tok(text, return_tensors='pt', padding=True).to(self.torch_device)
            assert len(trained_batch['input_ids'][0]) < 512, 'Tokenized batch too long!'
            trained_translated = self.trained_model.generate(**trained_batch, num_beams=1, early_stopping=False)
            trained_translated_txt = self.trained_tok.batch_decode(trained_translated, skip_special_tokens=True)
        # elif self.backend == 'fairseq':
        #     trained_translated_txt = self.trained_model.translate(text)
        return trained_translated_txt

    def translate(self, s):
        bs = self.bs
        t = time()
        res_arr = []
        batch_s = s.split('\n')
        if bs != -1:
            n_batches = int(np.ceil(len(batch_s) / bs))
            for b in trange(n_batches):
                start = b*bs
                end = start+bs
                curr_batch = batch_s[start:end]
                res_arr.extend(self.get_translated_text(curr_batch))
                with open(f'progress/{self.timestamp}.txt', 'w') as f:
                    f.write(f'{b+1}/{n_batches}')
        else:
            res_arr = self.get_translated_text(s)
        result = '\n'.join(res for res in res_arr)
        print(f'Time taken: {time() - t}, batch size: {bs}')
        return result

    def __call__(self, mimetype, content):
        res = {'en': 'Translation 1', 'he': 'המקור אינו קובץ טקסט'}
        if mimetype.startswith("text"):
            txt = content.decode()
            res['en'] = self.translate(txt)
            res['he'] = txt
        elif mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            processed_content = process(content)
            split_txt = split_content(processed_content, max_words=200, source='he')
            txt = join_text(split_txt)
            translated_txt = self.translate(txt)
            txt = '\n\n'.join(txt.split('\n'))
            translated_txt = '\n\n'.join(translated_txt.split('\n'))
            res['en'] = translated_txt
            res['he'] = txt
        os.remove(f'progress/{self.timestamp}.txt')
        return res


model_setup()
