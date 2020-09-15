import requests
import re
import argparse
import tqdm
import sys
import os
from datetime import datetime

from zohar_download_article import download, MissingLanguage
from zohar_preprocess_file import process, Options
from zohar_split_heuristic import split_and_save
from zohar_clear_dirty import discard_non_matching
from zohar_create_summary import save_summary

SAMPLE_URL = 'https://kabbalahmedia.info/he/sources/yUcfylRm'
LINK_REGEX = re.compile(r'div id\=\"title\-[A-Za-z0-9]+\"')

def sources_list(base=SAMPLE_URL):
    "This functions extract list of article ids from kabbalahmedia.info web page"

    LINK_REGEX = re.compile(r'div id\=\"title\-[A-Za-z0-9]+\"')
    
    src = requests.get(base).text
    links = LINK_REGEX.findall(src)
    
    return list({link[len('div id="title-'):-1] for link in links})

def utctime():
    "this function returns utc time string"

    return datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S_%f")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=SAMPLE_URL, help="root tree url")
    parser.add_argument("--dest", default='zohar/', help="destination directory")
    parser.add_argument("--skip-process", dest='skip', action='store_true', help="skip processing (only download)")
    parser.add_argument("--no-skip-process", dest='skip', action='store_false', help="do not skip processing (default)")

    parser.add_argument("--chunk", choices=['paragraphs', 'sentences', 'chars', 'joined'], default='paragraphs')
    parser.add_argument("--n_chars_en", help='number of chars in an english phrase', default=255)
    parser.add_argument("--n_chars_he", help='number of chars in a hebrew phrase', default=225)

    parser.add_argument("--discard-non-matching", help='discard letters (Ot) with different number of chunks in hebrew and in english in split heuristic',
                        action='store_true', dest='strict')
    parser.add_argument("--no-discard-non-matching", help='do not discard letters (Ot) with different number of chunks in hebrew and in english split heuristic',
                        action='store_false', dest='strict')

    parser.add_argument("--en_words_threshold", help="number of words below which the Ot is not split (pass 0 to skip split heuristic)", default=200)
    parser.add_argument("--split_extension", help="extension of split files", default='.split.txt')

    parser.add_argument("--min_ratio", help="minimum english/hebrew ratio", default=0.5)
    parser.add_argument("--max_ratio", help="maximum english/hebrew ratio", default=2.0)

    parser.add_argument("--summary_name", help="html summary file name", default="summary.html")

    parser.set_defaults(skip=False)
    parser.set_defaults(strict=True)

    args = parser.parse_args()
    sources = sources_list(args.root)

    progress = tqdm.tqdm(range(len(sources)))
    for src, _ in zip(sources, progress):
        try:
            paths, title, base = download(src, args.dest)
            if args.skip:
                continue

            lang_paths = dict(paths)
            en_path = lang_paths['en']
            he_path = lang_paths['he']

            ts = utctime()
            postfix = '.' + ts + '.txt'
            opts = [Options(en_path, args.chunk, 'en', args.n_chars_en),
                    Options(he_path, args.chunk, 'he', args.n_chars_he)]
            process(opts, postfix)

            # en_split = en_path + '.' + ts + args.split_extension
            # he_split = he_path + '.' + ts + args.split_extension
            en_split = en_path + '.' + src + args.split_extension
            he_split = he_path + '.' + src + args.split_extension
            en_path += postfix
            he_path += postfix

            sep = '\n'
            if args.en_words_threshold:
                atomic_line = args.chunk != 'joined'
                split_and_save(en_path, he_path, args.en_words_threshold, atomic_line, en_split, he_split)

                en_path = en_split
                he_path = he_split
                sep = '\n'

            if args.strict:
                discard_non_matching(en_path, he_path, sep)

            summary = os.path.join(base, args.summary_name)
            with open(summary, 'w', encoding='utf-8') as f:
                save_summary(en_path, he_path, sep, args.min_ratio, args.max_ratio, title, ts, f)

        except MissingLanguage:
            continue
        except Exception as e:
            print('Failed downloading', src, file=sys.stderr)
            raise

if __name__ == "__main__":
    main()
