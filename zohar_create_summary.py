from zohar_split_heuristic import letters_chunks
import argparse
import sys
import regexes
import re

def highlight(text, lang):
    "Searches for text indended to be highlighted using language specific regex"

    if not text:
        return ''

    summary = ''
    for regex in regexes.REGEXES[lang].HIGHLIGHT:
        for m in re.finditer(regex, text):
            summary += '<b>' + text[m.start():m.end()] + '</b> ' + f'{m.start()}:{m.end()}' + '<br/>'

    return summary

def summary(eng, heb, sep, min_ratio, max_ratio):
    "Creates letter (Ot) html summary"

    letters = letters_chunks(eng, heb)

    for letter, en, he in letters:
        en_chunks = en.split(sep) if en else []
        he_chunks = he.split(sep) if he else []

        valid = True
        if len(en_chunks) != len(he_chunks):
            valid = False
        else:
            for e, h in zip(en_chunks, he_chunks):
                if not e or not h:
                    value = False
                    break
                if not (min_ratio < len(e) / len(h) < max_ratio):
                    value = False
                    break

        comments = highlight(en, 'en') + highlight(he, 'he')
        yield (letter, len(en_chunks), len(he_chunks), valid, comments)

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
    print('<tr><th>Item</th><th>HE #Chunks</th><th>EN #Chunks</th><th>Valid?</th><th>Comments</th>', file=output)

    for letter, n_en, n_he, valid, comments in rows:
        print(f'<tr><td>{letter}</td><td>{n_he}</td><td>{n_en}</td><td>{valid}</td><td>{comments}</td></tr>', file=output)

    print('</table></body></html>', file=output)

def save_summary(eng, heb, sep, minr, maxr, title, ts, output):
    "Creates the summary and prints it to the output file"

    with open(eng) as en, open(heb) as he:
         rows = summary(en.read(), he.read(), sep, minr, maxr)

    webpage(rows, minr, maxr, ts, title, output)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("english_file", help="path to file containing english text")
    parser.add_argument("hebrew_file", help="path to file contating hebrew text")
    parser.add_argument("--sep", help="separator character", default='\n\n')
    parser.add_argument("--min_ratio", help="minimum english/hebrew ratio", default=0.5)
    parser.add_argument("--max_ratio", help="maximum english/hebrew ratio", default=2.0)
    parser.add_argument("--title", help="article title", default='')
    parser.add_argument("--timestamp", help="file creation timestamp", default='')

    args = parser.parse_args()
    save_summary(args.english_file, args.hebrew_file, args.sep, args.min_ratio,
                 args.max_ratio, args.title, args.timestamp, sys.stdout)

if __name__ == "__main__":
    main()
