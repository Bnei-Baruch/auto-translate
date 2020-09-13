import argparse
import regexes
import math
import re

from zohar_split_heuristic import append, save_file, letters_chunks

import sys

def discard_non_matching(eng, heb, sep):
    "discards all letters with non-consitetnt chunks number"

    with open(eng, encoding='utf-8') as enf, open(heb, encoding='utf-8') as hef:
        letters = letters_chunks(enf.read(), hef.read())

    en_letters = []
    he_letters = []

    for letter, en, he in letters:
        en_chunks = len(en.split(sep)) if en else 0
        he_chunks = len(he.split(sep)) if he else 0

        if en_chunks != he_chunks:
            continue

        append(en_letters, letter, en, 'en')
        append(he_letters, letter, he, 'he')

    save_file(en_letters, eng)
    save_file(he_letters, heb)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("english_file", help="path to file containing english text")
    parser.add_argument("hebrew_file", help="path to file contating hebrew text")
    parser.add_argument("--sep", help="chunks separator", default='\n')

    args = parser.parse_args()
    discard_non_matching(args.english_file, args.hebrew_file, args.sep)

if __name__ == "__main__":
    main()
