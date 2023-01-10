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
from tqdm import trange, tqdm


def model_setup():
    models = {'he_en_zohar_V1':
                  'https://drive.google.com/u/0/uc?id=1pbiJNqtQ3W4fJmk3cH-8sD-mZ7eUp4JK&export=download',
              'en_sp_zohar_V1':
                  'https://drive.google.com/u/0/uc?id=195HjThVR1Y0KI93PvLbqpNXw2Iqg4stk&export=download',
              'he_sp_zohar_V1':
                  'https://drive.google.com/u/0/uc?id=1IVPls1YJyJFhrfArKSNkUrZJiQghpT9o&export=download',
              'he_en_zohar_V2':
                  'https://drive.google.com/u/0/uc?id=1ztkSltdH6j3yfTTModxH8aSkUA_lJlJW&export=download',
              }
    for model_name, model_url in models.items():
        is_old = model_name.endswith('V1')
        if not os.path.exists(f'models/{model_name}'):
            output = 'model.zip'
            gdown.download(model_url, output, quiet=False)
            with ZipFile(output, 'r') as zipf:
                zipf.extractall()
            path = 'ds_combined_ft_optimized'
            if is_old: path = 'content/model'
            shutil.move(path, f'models/{model_name}')
            if is_old: shutil.rmtree('content')


def process(content, lang='he'):
    output = paragraphs(content)
    output = replace(output, lang)
    return output


def split_content(content, max_words, source):
    res = split_letters_source(content, max_words=max_words, source=source)
    output, words_processed, words_total = res
    if words_total == 0:
        raise Exception('No words found, bad format or wrong language maybe?')
    print(f'Processed {words_processed} words out of {words_total} ({100 * words_processed / words_total}%) with '
          f'max_words {max_words}')
    return output


class TranslationModel:
    def __init__(self, model, timestamp, args, write=True, rel_path='models/'):
        self.model = model
        parts = model.split('_')
        self.source = parts[0]
        self.target = parts[1]
        self.timestamp = timestamp
        self.write = write
        if self.write:
            with open(f'progress/{self.timestamp}.txt', 'w') as f:
                f.write('0/0')
        self.bs = args.bs
        self.backend = args.backend
        if args.threads != -1:
            torch.set_num_threads(args.threads)
        print(f'Running with {torch.get_num_threads()} threads.')
        mname = rel_path + model
        self.torch_device = 'cpu'
        self.trained_model = AutoModelForSeq2SeqLM.from_pretrained(mname).to(self.torch_device)
        self.trained_tok = AutoTokenizer.from_pretrained(mname, is_fast=True)

    def get_translated_text(self, text):
        text = [t for t in text if t]
        trained_translated_txt = ['']
        if not text: return trained_translated_txt
        trained_batch = self.trained_tok(text, return_tensors='pt', padding=True).to(self.torch_device)
        assert len(trained_batch['input_ids'][0]) < 512, 'Tokenized batch too long!'
        trained_translated = self.trained_model.generate(**trained_batch, num_beams=1)
        trained_translated_txt = self.trained_tok.batch_decode(trained_translated, skip_special_tokens=True)
        return trained_translated_txt

    def translate(self, s):
        bs = self.bs
        tm = time()
        res_arr = []
        batch_s = np.array([t for t in s.split('\n') if t])
        lns = np.array([len(t.split()) for t in batch_s])
        # argsort for batching and then invert it
        argsort1 = lns.argsort()
        argsort2 = argsort1.argsort()
        batch_s = batch_s[argsort1]
        if bs != -1:
            n_batches = int(np.ceil(len(batch_s) / bs))
            for b in trange(n_batches):
                start = b * bs
                end = start + bs
                curr_batch = batch_s[start:end]
                res_arr.extend(self.get_translated_text(curr_batch))
                if self.write:
                    with open(f'progress/{self.timestamp}.txt', 'w') as f:
                        f.write(f'{b + 1}/{n_batches}')
        else:
            res_arr = self.get_translated_text(s)
        res_arr = np.array(res_arr)[argsort2]
        result = '\n'.join(res for res in res_arr)
        print(f'Time taken: {time() - tm}, batch size: {bs}')
        return result

    def __call__(self, mimetype, content):
        res = {'target': 'Translation 1', 'source': 'Not a text file'}
        if mimetype == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            original_content = process(content)
            max_words = 350 if self.model.endswith('V2') else 200
            split_txt = split_content(original_content, max_words=max_words, source=self.source)
            content = join_text(split_txt)
            tok_ln = self.trained_tok(content.split('\n'), return_length=True)['length']
            while max(tok_ln) >= 512:
                max_words -= 50
                split_txt = split_content(original_content, max_words=max_words, source=self.source)
                content = join_text(split_txt)
                tok_ln = self.trained_tok(content.split('\n'), return_length=True)['length']
        translated_txt = self.translate(content)
        txt = '\n\n'.join(content.split('\n'))
        translated_txt = '\n\n'.join(translated_txt.split('\n'))
        res['target'] = translated_txt.strip()
        res['source'] = txt.strip()
        # os.remove(f'progress/{self.timestamp}.txt')
        return res


if __name__ == '__main__':
    model_setup()