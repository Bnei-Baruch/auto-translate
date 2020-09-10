from zohar_split_heuristic import letters_chunks
import argparse
import sys


def diff(eng, heb, sep):
    letters = letters_chunks(eng, heb)
    print('<html><head><title>difftool</title></head><body>')

    for letter, en, he in letters:
        en_chunks = en.strip().split(sep) if en else ()
        he_chunks = he.strip().split(sep) if he else ()

        engen = (chunk for chunk in en_chunks)
        hegen = (chunk for chunk in he_chunks)

        print('<table border="5"><tr><th colspan=2>', letter, '</th></tr>')
        for en_txt, he_txt in zip(engen, hegen):
            print('<tr>')
            print('<td style="text-direction: ltr; width: 50%">')
            print(en_txt)
            print('</td><td style="text-direction: rtl">')
            print(he_txt)
            print('</td></tr>')

        for en_txt in engen:
            print('<tr><td style="text-direction: ltr; width: 50%">')
            print(en_txt)
            print('</td><td></td></tr>')

        for he_txt in hegen:
            print('<tr><td></td><td style="text-direction: rtl">')
            print(he_txt)
            print('</td></tr>')
    print('</table>')

    print('</body></html>')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("english_file")
    parser.add_argument("hebrew_file")
    parser.add_argument("--sep", default='\n')

    args = parser.parse_args()

    with open(args.english_file) as en, open(args.hebrew_file) as he:
        diff(en.read(), he.read(), args.sep)

if __name__ == "__main__":
    main()
