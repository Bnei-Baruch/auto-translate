from zohar_split_heuristic import letters_chunks
import argparse
import sys


def diff(tgt_doc, src_doc, langs, sep):
    letters = letters_chunks(tgt_doc, src_doc)
    print('<html><head><title>difftool</title></head><body>')

    for letter, tgt, src in letters:
        tgt_chunks = tgt.strip().split(sep) if tgt else ()
        src_chunks = src.strip().split(sep) if src else ()

        tgtgen = (chunk for chunk in tgt_chunks)
        srcgen = (chunk for chunk in src_chunks)

        print('<table border="5"><tr><th colspan=2>', letter, '</th></tr>')
        for tgt_txt, src_txt in zip(tgtgen, srcgen):
            print('<tr>')
            print('<td style="text-direction: ltr; width: 50%">')
            print(tgt_txt)
            print('</td><td style="text-direction: rtl">')
            print(src_txt)
            print('</td></tr>')

        for tgt_txt in tgtgen:
            print('<tr><td style="text-direction: ltr; width: 50%">')
            print(tgt_txt)
            print('</td><td></td></tr>')

        for src_txt in srcgen:
            print('<tr><td></td><td style="text-direction: rtl">')
            print(src_txt)
            print('</td></tr>')
    print('</table>')

    print('</body></html>')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default='he', help="source language")
    parser.add_argument("--target", default='en', help="target language")
    parser.add_argument("target_file")
    parser.add_argument("source_file")
    parser.add_argument("--sep", default='\n')

    args = parser.parse_args()
    langs = (args.source, args.target)
    with open(args.target_file) as tgt, open(args.source_file, encoding='utf-8') as src:
        diff(tgt.read(), src.read(), langs, args.sep)

if __name__ == "__main__":
    main()
