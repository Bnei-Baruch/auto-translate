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

def letters_chunks(tgt_doc, src_doc, langs):
    "returns list of triples containing letter number (Ot), english content and hebrew content"

    source, target = langs
    tgt = dict(split_by_letters(tgt_doc, target))
    src = dict(split_by_letters(src_doc, source))

    letters = list(sorted(set(tgt.keys()) | set(src.keys())))
    res = [(letter, tgt.get(letter), src.get(letter)) for letter in letters]
    return res

def append(output, letter, content, lang):
    "append letter entry to output list"

    if lang == 'he':
        output.append((f'.{letter}', content))
    else:
        output.append((f'{letter})', content))

def split_letters(tgt_doc, src_doc, langs, max_tgt_words, atomic_line):
    """Runs split heuristics. The heuristic works as follows:
            If the number of english words is smaller than max_tgt_words, the content is left as is.
            Otherwise, the content is divided into chunk of size slightly larger
            than max_tgt_words (it is larger because atomic parts of the text are not split)"""
    source, target = langs
    letters = letters_chunks(tgt_doc, src_doc, langs)
    output_tgt = []
    output_src = []

    for letter, tgt, src in letters:
        if not tgt and src:
            # append(output_src, letter, he, 'he')
            continue
        if not src and tgt:
            # append(output_tgt, letter, en, 'en')
            continue
        if not src and not tgt:
            continue

        n_tgt = len(tgt.split())
        if n_tgt <= max_tgt_words:
            append(output_tgt, letter, tgt, target)
            append(output_src, letter, src, source)
            continue

        n_chunks = math.ceil(n_tgt / max_tgt_words)

        tgt_parts = tgt.split('\n') if atomic_line else tgt.split()
        src_parts = src.split('\n') if atomic_line else src.split()

        tgt_chunk = math.ceil(len(tgt_parts) / n_chunks)
        src_chunk = math.ceil(len(src_parts) / n_chunks)

        tgt_chunks = ['\n'.join(tgt_parts[i*tgt_chunk:(i+1)*tgt_chunk]) for i in range(n_chunks)]
        tgt_chunks = [re.sub(r'\n+', '', chunk) for chunk in tgt_chunks]
        src_chunks = ['\n'.join(src_parts[i*src_chunk:(i+1)*src_chunk]) for i in range(n_chunks)]
        src_chunks = [re.sub(r'\n+', '', chunk) for chunk in src_chunks]

        assert len(tgt_chunks) == len(src_chunks)

        tgt_final_chunks, src_final_chunks = [], []
        for src_c, tgt_c in zip(src_chunks, tgt_chunks):
            if src_c.strip() and tgt_c.strip():
                tgt_final_chunks.append(tgt_c)
                src_final_chunks.append(src_c)

        assert len(tgt_final_chunks) == len(src_final_chunks)

        tgt_full = '\n'.join(tgt_final_chunks)
        tgt_full = re.sub(r'\n+', '\n', tgt_full).strip()
        src_full = '\n'.join(src_final_chunks)
        src_full = re.sub(r'\n+', '\n', src_full).strip()

        assert tgt_full.count('\n') == src_full.count('\n')
        # if tgt_full.count('\n') != src_full.count('\n'):
        #     print('LINES MISMATCH - SKIPPING LETTER')
        #     continue

        append(output_tgt, letter, tgt_full, target)
        append(output_src, letter, src_full, source)

    assert len(output_tgt) == len(output_src)
    return output_tgt, output_src

def save_file(letters, path):
    with open(path, 'w', encoding='utf-8') as f:
        for letter, content in letters:
            print(letter, end=' ', file=f)
            print(content, file=f)

def split_and_save(tgt_doc, src_doc, langs, tgt_words_threshold, atomic_line, tgt_out, src_out):
    "runs split heuristic and save the output to a file"

    with open(tgt_doc, encoding='utf-8') as tgt, open(src_doc, encoding='utf-8') as src:
        output_tgt, output_src = split_letters(tgt.read(), src.read(), langs, tgt_words_threshold, atomic_line)

    save_file(output_tgt, tgt_out)
    save_file(output_src, src_out)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default='he', help="source language")
    parser.add_argument("--target", default='en', help="target language")
    parser.add_argument("target_file", help="path to file containing target text")
    parser.add_argument("source_file", help="path to file containing source text")
    parser.add_argument("--output_postfix", help="postfix of the output file names", default='.split.txt')
    parser.add_argument("--tgt_words_threshold", help="number of words below which the Ot is not split", default=512)

    parser.add_argument("--atomic_line", dest='atomic_line', action='store_true', help="make lines atomic (default)")
    parser.add_argument("--no-atomic-line", dest='atomic_line', action='store_false', help="make words atomic")
    parser.set_defaults(atomic_line=True)

    args = parser.parse_args()
    src_output = args.source_file + args.output_postfix
    tgt_output = args.target_file + args.output_postfix
    split_and_save(args.target_file, args.source_file, (args.source, args.target),
                   args.tgt_words_threshold, args.atomic_line, tgt_output, src_output)

if __name__ == "__main__":
    main()
