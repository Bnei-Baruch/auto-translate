import argparse
import regexes
import math
import re

from zohar_split_heuristic import append, save_file, letters_chunks

import sys

def discard_non_matching(tgt_doc, src_doc, langs, sep):
    "discards all letters with non-consistent chunks number"
    source, target = langs
    total_discarded, total_kept = 0, 0
    with open(tgt_doc, encoding='utf-8') as tgt_f, open(src_doc, encoding='utf-8') as src_f:
        letters = letters_chunks(tgt_f.read(), src_f.read(), langs)

    tgt_letters = []
    src_letters = []

    for letter, tgt, src in letters:
        tgt = re.sub('\n+', '\n', tgt)
        src = re.sub('\n+', '\n', src)
        tgt_chunks = len(tgt.split(sep)) if tgt else 0
        src_chunks = len(src.split(sep)) if src else 0

        if tgt_chunks != src_chunks:
            total_discarded += src_chunks
            continue

        total_kept += src_chunks
        append(tgt_letters, letter, tgt, target)
        append(src_letters, letter, src, source)

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

    args = parser.parse_args()
    discard_non_matching(args.target_file, args.source_file, (args.source, args.target), args.sep)

if __name__ == "__main__":
    main()