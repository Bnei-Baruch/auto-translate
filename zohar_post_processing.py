import argparse
import regexes
import math
import re
from zohar_split_heuristic import append, append_str, save_file, letters_chunks
import sys


def combine_discard_non_matching(tgt_doc, src_doc, langs, sep, threshold, combine_letters):
    source, target = langs
    total_discarded, total_kept = 0, 0
    with open(tgt_doc, encoding='utf-8') as tgt_f, open(src_doc, encoding='utf-8') as src_f:
        letters = letters_chunks(tgt_f.read(), src_f.read(), langs)

    tgt_letters = []
    src_letters = []
    tgt_one_chunk = ''
    src_one_chunk = ''
    prev_letter = 0
    if letters:
        prev_letter = letters[0][0]
    for letter, tgt, src in letters:
        if src is None or tgt is None:
            continue

        tgt = re.sub(r'\n+', '\n', tgt)
        tgt = re.sub(r' +', ' ', tgt).replace(' . ', '. ')
        src = re.sub(r'\n+', '\n', src)
        src = re.sub(r' +', ' ', src).replace(' . ', '. ')
        tgt_chunks = len(tgt.split(sep)) if tgt else 0
        src_chunks = len(src.split(sep)) if src else 0

        if tgt_chunks != src_chunks:
            total_discarded += src_chunks
            continue

        if combine_letters:
            total_kept += src_chunks
            ln_tgt_chunk = len(tgt_one_chunk.split())
            ln_src_chunk = len(src_one_chunk.split())
            ln_tgt_curr = len(tgt.split())
            ln_src_curr = len(src.split())
            below_threshold = (ln_tgt_chunk+ln_tgt_curr) < threshold and (ln_src_chunk+ln_src_curr) < threshold

            if below_threshold and letter >= prev_letter:
                tgt_one_chunk = append_str(tgt_one_chunk, letter, tgt, target)
                src_one_chunk = append_str(src_one_chunk, letter, src, source)
            else:
                if tgt_one_chunk != '' and src_one_chunk != '':
                    append(tgt_letters, '', tgt_one_chunk, target)
                    append(src_letters, '', src_one_chunk, source)
                tgt_one_chunk = append_str('', letter, tgt, target)
                src_one_chunk = append_str('', letter, src, source)

            prev_letter = letter

        else:
            total_kept += src_chunks
            append(tgt_letters, letter, tgt, target)
            append(src_letters, letter, src, source)

    if combine_letters and tgt_one_chunk and src_one_chunk:
        append(tgt_letters, '', tgt_one_chunk, target)
        append(src_letters, '', src_one_chunk, source)

    save_file(tgt_letters, tgt_doc)
    save_file(src_letters, src_doc)
    return total_discarded, total_kept

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default='he', help="source language")
    parser.add_argument("--target", default='en', help="target language")
    parser.add_argument("target_file", help="path to file containing target text")
    parser.add_argument("source_file", help="path to file contating source text")
    parser.add_argument("--sep", help="chunks separator", default='\n')
    parser.add_argument("--words_threshold", help="number of words below which the Ot is not split (pass 0 to skip split heuristic)", default=300)
    parser.add_argument("--no-combine-letters", help='do not combine letters (Ot) up to the words threshold',
                        action='store_false', dest='combine_letters')

    parser.set_defaults(combine_letters=True)
    args = parser.parse_args()
    combine_discard_non_matching(args.target_file, args.source_file, (args.source, args.target),
                                 args.sep, args.words_threshold, combine_letters)

if __name__ == "__main__":
    main()
