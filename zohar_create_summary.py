from zohar_split_heuristic import letters_chunks
import argparse
import sys
import regexes
import re

def highlight(text, lang):
    "Searches for text intended to be highlighted using language specific regex"

    if not text:
        return ''

    summary = ''
    for regex in regexes.REGEXES[lang].HIGHLIGHT:
        for m in re.finditer(regex, text):
            summary += '<b>' + text[m.start():m.end()] + '</b> ' + f'{m.start()}:{m.end()}' + '<br/>'

    return summary

def summary(tgt_doc, src_doc, langs, sep, min_ratio, max_ratio):
    "Creates letter (Ot) html summary"

    source, target = langs
    letters = letters_chunks(tgt_doc, src_doc, langs)

    for letter, tgt, src in letters:
        tgt_chunks = tgt.split(sep) if tgt else []
        src_chunks = src.split(sep) if src else []

        valid = True
        if len(tgt_chunks) != len(src_chunks):
            valid = False
        else:
            for t, s in zip(tgt_chunks, src_chunks):
                if not t or not s:
                    value = False
                    break
                if not (min_ratio < len(t) / len(s) < max_ratio):
                    value = False
                    break

        comments = highlight(tgt, target) + highlight(src, source)
        yield (letter, len(tgt_chunks), len(src_chunks), valid, comments)

def webpage(rows, min_ratio, max_ratio, timestamp, title, output):
    "Creates html summary for all letters"

    print(f'<html><head><title>{title}</title></head><body>', file=output)

    print('<dl>', file=output)
    print('<dt>Article</dt>', '<dd>', title, '</dd>', sep='', file=output)
    print('<dt>Timestamp</dt>', '<dd>', timestamp, '</dd>', sep='', file=output)
    print('<dt>Minimum Ratio</dt>', '<dd>', min_ratio, '</dd>', sep='', file=output)
    print('<dt>Maximum Ratio</dt>', '<dd>', max_ratio, '</dd>', sep='', file=output)
    print('</dl>', file=output)

    print('<table cellspacing="0" border="1" width="100%">', file=output)
    print('<tr><th>Item</th><th>SOURCE #Chunks</th><th>TARGET #Chunks</th><th>Valid?</th><th>Comments</th>', file=output)

    for letter, n_tgt, n_he, valid, comments in rows:
        print(f'<tr><td>{letter}</td><td>{n_he}</td><td>{n_tgt}</td><td>{valid}</td><td>{comments}</td></tr>', file=output)

    print('</table></body></html>', file=output)

def save_summary(tgt_doc, src_doc, langs, sep, minr, maxr, title, ts, output):
    "Creates the summary and prints it to the output file"

    with open(tgt_doc, encoding='utf-8') as tgt, open(src_doc, encoding='utf-8') as src:
         rows = summary(tgt.read(), src.read(), langs, sep, minr, maxr)

    webpage(rows, minr, maxr, ts, title, output)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default='he', help="source language")
    parser.add_argument("--target", default='en', help="target language")
    parser.add_argument("target_file", help="path to file containing target text")
    parser.add_argument("source_file", help="path to file contating source text")
    parser.add_argument("--sep", help="separator character", default='\n')
    parser.add_argument("--min_ratio", help="minimum target/source ratio", default=0.5)
    parser.add_argument("--max_ratio", help="maximum target/source ratio", default=2.0)
    parser.add_argument("--title", help="article title", default='')
    parser.add_argument("--timestamp", help="file creation timestamp", default='')

    args = parser.parse_args()
    save_summary(args.target_file, args.source_file, (args.source, args.target), args.sep, args.min_ratio,
                 args.max_ratio, args.title, args.timestamp, sys.stdout)

if __name__ == "__main__":
    main()
