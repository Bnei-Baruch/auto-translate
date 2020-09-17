import requests
import re
import argparse
import tqdm
import sys
import os
import shutil
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
    parser.add_argument("--dest", default='zohar', help="destination directory")
    parser.add_argument("--source", default='he', help="source language")
    parser.add_argument("--target", default='en', help="target language")
    parser.add_argument("--skip-process", dest='skip', action='store_true', help="skip processing (only download)")
    parser.add_argument("--no-skip-process", dest='skip', action='store_false', help="do not skip processing (default)")

    parser.add_argument("--chunk", choices=['paragraphs', 'sentences', 'chars', 'joined'], default='paragraphs')
    parser.add_argument("--n_chars_tgt", help='number of chars in the target phrase', default=255)
    parser.add_argument("--n_chars_src", help='number of chars in the source phrase', default=225)

    parser.add_argument("--discard-non-matching", help='discard letters (Ot) with different number of chunks in hebrew and in english in split heuristic',
                        action='store_true', dest='strict')
    parser.add_argument("--no-discard-non-matching", help='do not discard letters (Ot) with different number of chunks in hebrew and in english split heuristic',
                        action='store_false', dest='strict')

    parser.add_argument("--words_threshold", help="number of words below which the Ot is not split (pass 0 to skip split heuristic)", default=140)
    parser.add_argument("--split_extension", help="extension of split files", default='.split.txt')

    parser.add_argument("--min_ratio", help="minimum target/source ratio", default=0.5)
    parser.add_argument("--max_ratio", help="maximum target/source ratio", default=2.0)

    parser.add_argument("--summary_name", help="html summary file name", default="summary.html")

    parser.set_defaults(skip=False)
    parser.set_defaults(strict=True)
    total_discarded, total_kept, total_letters_processed, total_letters = 0, 0, 0, 0
    args = parser.parse_args()
    sources = sources_list(args.root)
    langs = (args.source, args.target)
    block = 'en' in langs
    block_list = ['F2LYqFgK', 'lgUtBujx']
    dest_folder =f'{args.dest}_{args.source}_{args.target}'
    shutil.rmtree(dest_folder, ignore_errors=True)
    progress = tqdm.tqdm(range(len(sources)))
    for src, _ in zip(sources, progress):
        if block and src in block_list:
            continue
        try:
            paths, title, base = download(src, dest_folder, langs)
            if args.skip:
                continue

            lang_paths = dict(paths)
            tgt_path = lang_paths[args.target]
            src_path = lang_paths[args.source]

            ts = utctime()
            postfix = '.' + ts + '.txt'
            opts = [Options(tgt_path, args.chunk, args.target, args.n_chars_tgt),
                    Options(src_path, args.chunk, args.source, args.n_chars_src)]
            process(opts, postfix)

            # tgt_split = tgt_path + '.' + ts + args.split_extension
            # src_split = src_path + '.' + ts + args.split_extension
            tgt_split = tgt_path + '.' + src + args.split_extension
            src_split = src_path + '.' + src + args.split_extension
            tgt_path += postfix
            src_path += postfix

            sep = '\n'
            if args.words_threshold:
                atomic_line = args.chunk != 'joined'
                letters_processed, n_letters = split_and_save(tgt_path, src_path, langs,
                                                              args.words_threshold, atomic_line,
                                                              tgt_split, src_split)
                total_letters_processed += letters_processed
                total_letters += n_letters

                tgt_path = tgt_split
                src_path = src_split
                sep = '\n'

            if args.strict:
                discarded, kept = discard_non_matching(tgt_path, src_path, langs, sep)
                total_discarded += discarded
                total_kept += kept

            summary = os.path.join(base, args.summary_name)
            with open(summary, 'w', encoding='utf-8') as f:
                save_summary(tgt_path, src_path, langs,
                             sep, args.min_ratio, args.max_ratio, title, ts, f)

        except MissingLanguage:
            continue
        except Exception as e:
            print('Failed downloading', src, file=sys.stderr)
            raise

    if args.strict:
        print('# Letters processed, total letters:',
              total_letters_processed, total_letters, total_letters_processed/total_letters)
        print('Total chunks kept, discarded during validation:', total_kept, total_discarded)

if __name__ == "__main__":
    main()
