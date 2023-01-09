import requests
import re
import argparse
import tqdm
import sys
import os
import shutil
from datetime import datetime
from p_tqdm import p_map

from zohar_download_article import download, MissingLanguage
from zohar_preprocess_file import process, Options
from zohar_split_heuristic import split_and_save
from zohar_post_processing import combine_discard_non_matching
from zohar_create_summary import save_summary

SAMPLE_URL = 'https://kabbalahmedia.info/he/sources/yUcfylRm'
LINK_REGEX = re.compile(r'div id\=\"title\-[A-Za-z0-9]+\"')

SAMPLES_DEST = {'ALlyoveA': 'bs_hakdamot',
                'bbdFZ9R4': 'bs_igrot',
                'eKY6PhmO': 'bs_maamarim',
                'hFeGidcS': 'bs_shamati',
                'PBrkeif3': 'rabash_igrot',
                'M53FJnYF': 'rabash_maamarim',
                'jYQX6fmA': 'rabash_reshumot',
                }


def sources_list(base=SAMPLE_URL):
    "This functions extract list of article ids from kabbalahmedia.info web page"

    LINK_REGEX = re.compile(r'div id\=\"title\-[A-Za-z0-9]+\"')

    src = requests.get(base).text
    links = LINK_REGEX.findall(src)

    return list({link[len('div id="title-'):-1] for link in links})


def utctime():
    "this function returns utc time string"

    return datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S_%f")


def download_function(src_and_args):
    src, args = src_and_args
    dest_folder = f'{args.dest}_{args.source}_{args.target}'
    langs = (args.source, args.target)
    try:
        paths, filename, base = download(src, dest_folder, langs)
        return paths, filename, base, src
    except MissingLanguage:
        return
    except Exception as e:
        print('Failed downloading', src, file=sys.stderr)
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=SAMPLE_URL, help="root tree url")
    parser.add_argument("--dest", default='zohar', help="destination directory")
    parser.add_argument("--source", default='he', help="source language")
    parser.add_argument("--target", default='en', help="target language")
    parser.add_argument("--skip-process", dest='skip', action='store_true', help="skip processing (only download)")
    parser.add_argument("--no-skip-process", dest='skip', action='store_false', help="do not skip processing (default)")

    parser.add_argument("--chunk", choices=['paragraphs', 'sentences', 'chars', 'joined'], default='paragraphs')
    parser.add_argument("--n_chars_tgt", help='number of chars in the target phrase', default=3000)
    parser.add_argument("--n_chars_src", help='number of chars in the source phrase', default=3000)
    parser.add_argument("--split_ratio", help='only keep sentences which abide by this ratio, pass 0. to disable',
                        default=2.5)

    parser.add_argument("--discard-non-matching",
                        help='discard letters (Ot) with different number of chunks in hebrew and in english in split heuristic',
                        action='store_true', dest='strict')
    parser.add_argument("--no-discard-non-matching",
                        help='do not discard letters (Ot) with different number of chunks in hebrew and in english split heuristic',
                        action='store_false', dest='strict')
    parser.add_argument("--no-combine-letters", help='do not combine letters (Ot) up to the words threshold',
                        action='store_false', dest='combine_letters')
    parser.add_argument("--words_threshold",
                        help="number of words below which the Ot is not split (pass 0 to skip split heuristic)",
                        default=500)
    parser.add_argument("--split_extension", help="extension of split files", default='.split.txt')

    parser.add_argument("--min_ratio", help="minimum target/source ratio", default=0.4)
    parser.add_argument("--max_ratio", help="maximum target/source ratio", default=2.5)

    parser.add_argument("--summary_name", help="html summary file name", default="summary.html")
    for root, dest in SAMPLES_DEST.items():
        dest = 'kab_corpus'
        parser.set_defaults(skip=False)
        parser.set_defaults(strict=True)
        parser.set_defaults(combine_letters=False)
        parser.set_defaults(root='https://kabbalahmedia.info/he/sources/'+root, dest=dest)
        total_discarded, total_kept, total_letters_processed, total_letters = 0, 0, 0, 0
        args = parser.parse_args()
        sources = sources_list(args.root)
        langs = (args.source, args.target)
        block = 'en' in langs
        block_list = ['F2LYqFgK', 'lgUtBujx']
        dest_folder = f'{args.dest}_{args.source}_{args.target}'
        ## shutil.rmtree(dest_folder, ignore_errors=True)
        if block:
            sources = [s for s in sources if s not in block_list]
        all_res = p_map(download_function, [(s, args) for s in sources])
        all_res = [a for a in all_res if a is not None]
        for paths, filename, base, src in all_res:
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

            tgt_split = tgt_path + '.' + src + args.split_extension
            src_split = src_path + '.' + src + args.split_extension
            tgt_path += postfix
            src_path += postfix

            sep = '\n'
            if args.words_threshold:
                atomic_line = args.chunk != 'joined'
                letters_processed, n_letters = split_and_save(tgt_path, src_path, langs,
                                                              args.words_threshold, atomic_line,
                                                              tgt_split, src_split, args.split_ratio)
                total_letters_processed += letters_processed
                total_letters += n_letters

                tgt_path = tgt_split
                src_path = src_split
                sep = '\n'

            if args.strict:
                discarded, kept = combine_discard_non_matching(tgt_path, src_path, langs, sep,
                                                               args.words_threshold, args.combine_letters)
                total_discarded += discarded
                total_kept += kept

            summary = os.path.join(base, args.summary_name)
            with open(summary, 'w', encoding='utf-8') as f:
                save_summary(tgt_path, src_path, langs,
                             sep, args.min_ratio, args.max_ratio, filename, ts, f)
        if args.strict:
            print('# Words processed, total words:',
                  total_letters_processed, total_letters, total_letters_processed / total_letters)
            print('Total chunks kept, discarded during validation:', total_kept, total_discarded)


if __name__ == "__main__":
    main()
