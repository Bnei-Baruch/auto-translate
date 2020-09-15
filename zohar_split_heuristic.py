import argparse
import regexes
import math
import re

import sys

def keep_digit(s):
    "keeps only digits in the input string and converts them to int"

    return int(re.sub('[^0-9]', '', s))

def split_by_letters(contents, lang):
    "splits the input string by letters (letter = Ot)"

    item = regexes.REGEXES[lang].ITEM

    parts = re.split(f'({item})', contents, flags=re.MULTILINE)
    keys = [keep_digit(key) for key in parts[1::2]]
    values = parts[2::2]
    assert len(keys) == len(values)
    return zip(keys, values)

def letters_chunks(eng, heb):
    "returns list of triples containing letter number (Ot), english content and hebrew content"

    en = dict(split_by_letters(eng, 'en'))
    he = dict(split_by_letters(heb, 'he'))

    letters = list(sorted(set(en.keys()) | set(he.keys())))
    return [(letter, en.get(letter), he.get(letter)) for letter in letters]

def append(output, letter, content, lang):
    "append letter entry to output list"

    assert lang in ('he', 'en')

    if lang == 'he':
        output.append((f'.{letter}', content))
    else:
        output.append((f'{letter})', content))

def split_letters(eng, heb, max_en_words, atomic_line):
    """Runs split heuristics. The heuristic works as follows:
            If the number of english words is smaller than max_en_words, the content is left as is.
            Otherwise, the content is divided into chunk of size slightly larger
            than max_en_words (it is larger because atomic parts of the text are not split)"""

    letters = letters_chunks(eng, heb)
    output_en = []
    output_he = []

    for letter, en, he in letters:
        if not en and he:
            # append(output_he, letter, he, 'he')
            continue
        if not he and en:
            # append(output_en, letter, en, 'en')
            continue
        if not he and not en:
            continue

        n_en = len(en.split())
        if n_en <= max_en_words:
            append(output_en, letter, en, 'en')
            append(output_he, letter, he, 'he')
            continue

        n_chunks = math.ceil(n_en / max_en_words)

        en_parts = en.split('\n') if atomic_line else en.split()
        he_parts = he.split('\n') if atomic_line else he.split()

        he_chunk = math.ceil(len(he_parts) / n_chunks)
        en_chunk = math.ceil(len(en_parts) / n_chunks)

        en_chunks = ['\n'.join(en_parts[i*en_chunk:(i+1)*en_chunk]) for i in range(n_chunks)]
        en_chunks = [re.sub(r'\n+', '', chunk) for chunk in en_chunks]
        he_chunks = ['\n'.join(he_parts[i*he_chunk:(i+1)*he_chunk]) for i in range(n_chunks)]
        he_chunks = [re.sub(r'\n+', '', chunk) for chunk in he_chunks]

        assert len(en_chunks) == len(he_chunks)

        en_final_chunks, he_final_chunks = [], []
        for he_c, en_c in zip(he_chunks, en_chunks):
            if he_c and en_c:
                en_final_chunks.append(en_c)
                he_final_chunks.append(he_c)

        assert len(en_final_chunks) == len(he_final_chunks)

        en_full = '\n'.join(en_final_chunks)
        en_full = re.sub(r'\n+', '\n', en_full).strip()
        he_full = '\n'.join(he_final_chunks)
        he_full = re.sub(r'\n+', '\n', he_full).strip()

        assert en_full.count('\n') == he_full.count('\n')

        append(output_en, letter, en_full, 'en')
        append(output_he, letter, he_full, 'he')

    assert len(output_en) == len(output_he)
    return output_en, output_he

def save_file(letters, path):
    with open(path, 'w', encoding='utf-8') as f:
        for letter, content in letters:
            print(letter, end=' ', file=f)
            print(content, file=f)

def split_and_save(eng, heb, en_words_threshold, atomic_line, en_out, he_out):
    "runs split heuristic and save the output to a file"

    with open(eng, encoding='utf-8') as en, open(heb, encoding='utf-8') as he:
        output_en, output_he = split_letters(en.read(), he.read(), en_words_threshold, atomic_line)

    if he_out.split('.')[-3] == 'Uh0TFSOM':
        pass
    save_file(output_en, en_out)
    save_file(output_he, he_out)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("english_file", help="path to file containing english text")
    parser.add_argument("hebrew_file", help="path to file containing hebrew text")
    parser.add_argument("--output_postfix", help="postfix of the output file names", default='.split.txt')
    parser.add_argument("--en_words_threshold", help="number of words below which the Ot is not split", default=512)

    parser.add_argument("--atomic_line", dest='atomic_line', action='store_true', help="make lines atomic (default)")
    parser.add_argument("--no-atomic-line", dest='atomic_line', action='store_false', help="make words atomic")
    parser.set_defaults(atomic_line=True)

    args = parser.parse_args()
    he_output = args.hebrew_file + args.output_postfix
    en_output = args.english_file + args.output_postfix
    split_and_save(args.english_file, args.hebrew_file, args.en_words_threshold,
                   args.atomic_line, en_output, he_output)

if __name__ == "__main__":
    main()
