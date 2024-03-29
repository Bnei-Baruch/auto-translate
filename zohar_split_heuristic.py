import argparse
import regexes
import math
import re
from hebrew_numbers import gematria_to_int

import sys


def keep_digit(s):
    "keeps only digits in the input string and converts them to int"
    res = s
    if s:
        s = re.sub('[^0-9\u0590-\u05FF]', '', s)
        res = int(s) if s.isdigit() else gematria_to_int(s)
    return res


def split_by_letters(contents, lang):
    "splits the input string by letters (letter = Ot)"

    item = regexes.REGEXES[lang].ITEM
    parts = re.split(f'({item})', contents, flags=re.MULTILINE)
    if len(parts) <= 1 and lang == 'he':
        item = regexes.REGEXES[lang].ITEM_PAR
        parts = re.split(f'({item})', contents, flags=re.MULTILINE)
    if len(parts) <= 1 and len(contents.split()) <= 500:
        parts = ['', '', contents]
    keys = [keep_digit(key) for key in parts[1::2]]
    values = parts[2::2]
    assert len(keys) == len(values)
    return zip(keys, values)


def fix_letters(tgt_let, src_let):
    letters = []
    for t, s in zip(tgt_let, src_let):
        if t and not s:
            letters.append(t)
        elif s and not t:
            letters.append(s)
        elif not s and not t:
            letters.append('')
        else:
            letters.append(s)
    return letters


def letters_chunks(tgt_doc, src_doc, langs):
    "returns list of triples containing letter number (Ot), english content and hebrew content"
    res = []
    if not tgt_doc or not src_doc:
        return res
    if len(tgt_doc.split()) <= 500 and len(src_doc.split()) <= 500:
        res.append((-1, tgt_doc, src_doc))
    else:
        source, target = langs
        tgt_split = split_by_letters(tgt_doc, target)
        src_split = split_by_letters(src_doc, source)
        tgt = list(tgt_split)
        src = list(src_split)
        if len(tgt) == len(src):
            tgt_let = [t[0] for t in tgt]
            src_let = [s[0] for s in src]
            letters = fix_letters(tgt_let, src_let)
            res = [(letter, tgt[i][1], src[i][1]) for i, letter in enumerate(letters)]
        else:
            tgt = dict(split_by_letters(tgt_doc, target))
            src = dict(split_by_letters(src_doc, source))
            letters = [i for i in src.keys() if i in set(tgt.keys())]
            res = [(letter, tgt.get(letter), src.get(letter)) for letter in letters]
    return res


def append(output, letter, content, lang, letter_only_once=False):
    "append letter entry to output list"
    letter = str(letter)
    if letter == '' and content == '':
        pass
    if letter_only_once:
        if len(output) > 0:
            output.append(('', content))
            return
    if letter == '':
        output.append(('', content))
    elif lang == 'he':
        output.append((f'.{letter} ', content))
    else:
        output.append((f'{letter}) ', content))


def append_str(output, letter, content, lang):
    "append letter entry to output list"
    if lang == 'he':
        output += f'.{letter} {content.strip()} '
    else:
        output += f'{letter}) {content.strip()} '
    return output


def split_letters_source(src_doc, max_words, source):
    if source == 'ru':
        src_doc = src_doc.replace('«', '“').replace('»', '”')
    if source == 'he':
        src_doc = re.sub(r'[a-zA-Z]+', '', src_doc)
        src_doc = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', src_doc)
        src_doc = '.'.join(sent for sent in src_doc.split('.') if ('דף' not in sent and 'כרך' not in sent))
    else:
        src_doc = re.sub(r'[\u0590-\u05fe]+', '', src_doc)

    src_doc = src_doc.replace('שגיאה! הסימניה אינה מוגדרת', '')
    src_doc = re.sub('[\(\[].*?[\)\]]', '', src_doc)

    letters = letters_chunks(src_doc, src_doc, (source, source))
    words_total = 0
    words_processed = 0
    output_src = []
    for letter, _, src in letters:
        letter_src = []
        if not src:
            continue

        src_strip = re.sub(r'\n+', '.', src).strip()
        src_sents = [s + '.' for s in src_strip.split('.') if s]

        src_one = ''
        for src_current in src_sents:
            n_src = len(src_one.split())
            ln_src = len(src_current.split())
            words_total += ln_src
            if (n_src + ln_src) < max_words:
                src_one += src_current.strip() + ' '
            else:
                if src_one:
                    append(letter_src, letter, src_one, source, True)
                src_one = ''
                # assert ln_src < max_words, 'TOO LONG'
                src_one += src_current.strip() + ' '
            words_processed += ln_src

        if src_one:
            append(letter_src, letter, src_one.strip(), source, True)

        if letter_src:
            output_src.extend(letter_src)

    return output_src, words_processed, words_total


def split_letters_new(tgt_doc, src_doc, langs, max_words, atomic_line, ratio):
    """Runs split heuristics. The heuristic works as follows:
            If the number of english words is smaller than max_words, the content is left as is.
            Otherwise, the content is divided into chunk of size slightly larger
            than max_words (it is larger because atomic parts of the text are not split)"""
    source, target = langs
    use_ratio = ratio != 0.
    min_ratio = 1 / ratio if use_ratio else 0.
    max_ratio = ratio if use_ratio else 0.
    if target == 'ru': tgt_doc = tgt_doc.replace('«', '“').replace('»', '”')
    if source == 'ru': src_doc = src_doc.replace('«', '“').replace('»', '”')
    if target == 'he':
        tgt_doc = re.sub(r'[a-zA-Z]+', '', tgt_doc)
        tgt_doc = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', tgt_doc)
        tgt_doc = '.'.join(sent for sent in tgt_doc.split('.') if ('דף' not in sent and 'כרך' not in sent))
    else:
        tgt_doc = re.sub(r'[\u0590-\u05fe]+', '', tgt_doc)
    if source == 'he':
        src_doc = re.sub(r'[a-zA-Z]+', '', src_doc)
        src_doc = re.sub(r'[\u0591-\u05BD\u05BF-\u05C2\u05C4-\u05C7]', '', src_doc)
        src_doc = '.'.join(sent for sent in src_doc.split('.') if ('דף' not in sent and 'כרך' not in sent))
    else:
        src_doc = re.sub(r'[\u0590-\u05fe]+', '', src_doc)

    tgt_doc = tgt_doc.replace('שגיאה! הסימניה אינה מוגדרת', '')
    src_doc = src_doc.replace('שגיאה! הסימניה אינה מוגדרת', '')
    tgt_doc = re.sub('[\(\[].*?[\)\]]', '', tgt_doc)
    src_doc = re.sub('[\(\[].*?[\)\]]', '', src_doc)

    letters = letters_chunks(tgt_doc, src_doc, langs)
    # words_total = len(letters)
    words_total = 0
    words_processed = 0
    output_tgt = []
    output_src = []
    for letter, tgt, src in letters:
        letter_tgt = []
        letter_src = []
        if not tgt or not src:
            continue

        # tgt = re.sub(r'\d+', '', tgt)
        # src = re.sub(r'\d+', '', src)
        tgt_strip = re.sub(r'\n+', '\n', tgt).strip()
        src_strip = re.sub(r'\n+', '\n', src).strip()
        tgt_sents = tgt_strip.split('\n')
        src_sents = src_strip.split('\n')

        if len(tgt_sents) != len(src_sents):
            tgt_no_linebreak = tgt_strip.replace('\n', ' ').strip()
            # tgt_sents = tgt_no_linebreak.replace('.’', '’.').replace('.”', '”.').replace('.’”', '’”.').split('. ')
            src_no_linebreak = src_strip.replace('\n', ' ').strip()
            # src_sents = src_no_linebreak.replace('.’', '’.').replace('.”', '”.').replace('.’”', '’”.').split('. ')

            # if len(tgt_sents) != len(src_sents):
            n_tgt = len(tgt_strip.split())
            n_src = len(src_strip.split())
            words_total += n_src
            ratio = True if not use_ratio else min_ratio < (n_tgt / n_src) < max_ratio
            if n_tgt < max_words and n_src < max_words and ratio:
                words_processed += n_src
                append(output_tgt, letter, tgt_no_linebreak, target, True)
                append(output_src, letter, src_no_linebreak, source, True)
            continue

        tgt_one, src_one = '', ''
        for tgt_current, src_current in zip(tgt_sents, src_sents):
            n_tgt = len(tgt_one.split())
            ln_tgt = len(tgt_current.split())
            n_src = len(src_one.split())
            ln_src = len(src_current.split())
            words_total += ln_src
            ratio = True if not use_ratio else min_ratio < (ln_tgt / ln_src) < max_ratio
            if (n_tgt + ln_tgt) < max_words and (n_src + ln_src) < max_words and ratio:
                tgt_one += ' ' + tgt_current
                src_one += ' ' + src_current
            else:
                if tgt_one and src_one:
                    words_processed += n_src
                    append(letter_tgt, letter, tgt_one, target, True)
                    append(letter_src, letter, src_one, source, True)
                tgt_one, src_one = '', ''
                if ln_tgt < max_words and ln_src < max_words and ratio:
                    tgt_one += ' ' + tgt_current
                    src_one += ' ' + src_current

        if tgt_one and src_one:
            words_processed += len(src_one.split())
            append(letter_tgt, letter, tgt_one, target, True)
            append(letter_src, letter, src_one, source, True)

        if letter_tgt and letter_src:
            output_tgt.extend(letter_tgt)
            output_src.extend(letter_src)

    assert len(output_tgt) == len(output_src)
    return output_tgt, output_src, words_processed, words_total


def join_text(letters):
    s = ''
    for letter, content in letters:
        letter = str(letter)
        content = content.strip()
        if letter and content:
            curr_s = letter if not '-1' in letter else '.'
            s += curr_s + content + '\n'
    return s


def save_file(letters, path):
    with open(path, 'w', encoding='utf-8') as f:
        for letter, content in letters:
            letter = str(letter)
            content = content.strip()
            s = '' if '-1' in letter else letter
            print(s + content, file=f)


def split_and_save(tgt_doc, src_doc, langs, words_threshold, atomic_line, tgt_out, src_out, split_ratio):
    "runs split heuristic and save the output to a file"

    with open(tgt_doc, encoding='utf-8') as tgt, open(src_doc, encoding='utf-8') as src:
        res = split_letters_new(tgt.read(), src.read(), langs, words_threshold, atomic_line, split_ratio)
        output_tgt, output_src, letters_processed, letters_total = res

    save_file(output_tgt, tgt_out)
    save_file(output_src, src_out)

    return letters_processed, letters_total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default='he', help="source language")
    parser.add_argument("--target", default='en', help="target language")
    parser.add_argument("target_file", help="path to file containing target text")
    parser.add_argument("source_file", help="path to file containing source text")
    parser.add_argument("--output_postfix", help="postfix of the output file names", default='.split.txt')
    parser.add_argument("--words_threshold", help="number of words below which the Ot is not split", default=512)
    parser.add_argument("--split_ratio", help='only keep sentences which abide by this ratio, pass 0. to disable',
                        default=2.0)
    parser.add_argument("--atomic_line", dest='atomic_line', action='store_true', help="make lines atomic (default)")
    parser.add_argument("--no-atomic-line", dest='atomic_line', action='store_false', help="make words atomic")
    parser.set_defaults(atomic_line=True)

    args = parser.parse_args()
    src_output = args.source_file + args.output_postfix
    tgt_output = args.target_file + args.output_postfix
    split_and_save(args.target_file, args.source_file, (args.source, args.target),
                   args.words_threshold, args.atomic_line, tgt_output, src_output, args.split_ratio)


if __name__ == "__main__":
    main()
