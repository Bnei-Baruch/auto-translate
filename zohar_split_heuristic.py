import argparse
import regexes_en
import regexes_he
import math
import re

import sys

REGEXES = {'he': regexes_he, 'en': regexes_en}

def keep_digit(s):
    return int(re.sub('[^0-9]', '', s))

def split_by_letters(contents, lang):
    item = REGEXES[lang].ITEM

    parts = re.split(f'({item})', contents, flags=re.MULTILINE)
    keys = [keep_digit(key) for key in parts[1::2]]
    values = parts[2::2]
    assert len(keys) == len(values)
    return zip(keys, values)

def letters_chunks(eng, heb):
    en = dict(split_by_letters(eng, 'en'))
    he = dict(split_by_letters(heb, 'he'))

    letters = list(sorted(set(en.keys()) | set(he.keys())))
    return [(letter, en.get(letter), he.get(letter)) for letter in letters]

def split_letters(eng, heb, max_en_words):
    letters = letters_chunks(eng, heb)
    output_en = []
    output_he = []

    for letter, en, he in letters:
        if not en and he:
            output_he.append((f'.{letter}', [he]))
            continue
        if not he and en:
            output_en.append((f'{letter})', [en]))
            continue
        if not he and not he:
            continue

        n_en = len(en.split())
        if n_en <= max_en_words:
            output_he.append((f'{letter}', [en]))
            output_en.append((f'.{letter})', [he]))
            continue

        n_chunks = math.ceil(n_en / max_en_words)

        en_parts = en.split('\n')
        he_parts = he.split('\n')

        he_chunk = math.ceil(len(he_parts) / n_chunks)
        en_chunk = math.ceil(len(en_parts) / n_chunks)

        en_chunks = ['\n'.join(en_parts[i*en_chunk:(i+1)*en_chunk]) for i in range(n_chunks)]
        he_chunks = ['\n'.join(he_parts[i*he_chunk:(i+1)*he_chunk]) for i in range(n_chunks)]

        output_en.append((f'{letter})', '\n\n'.join(en_chunks)))
        output_he.append((f'.{letter}', '\n\n'.join(he_chunks)))

    return output_en, output_he

def save_file(letters, path, postfix):
    with open(path + postfix, 'w') as f:
        for letter, content in letters:
            print(letter, end=' ', file=f)
            print(content, file=f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("english_file", help="path to file containing english text")
    parser.add_argument("hebrew_file", help="path to file contating hebrew text")
    parser.add_argument("--output_postfix", help="postfix of the output file names", default='.split.txt')
    parser.add_argument("--en_words_threshold", help="number of words below which the Ot is not split", default=512)

    args = parser.parse_args()

    with open(args.english_file) as en, open(args.hebrew_file) as he:
        output_en, output_he = split_letters(en.read(), he.read(), args.en_words_threshold)

    save_file(output_en, args.english_file, args.output_postfix)
    save_file(output_he, args.hebrew_file, args.output_postfix)

if __name__ == "__main__":
    main()
