import argparse
import regexes_en
import regexes_he
import re

import sys

REGEXES = {'he': regexes_he, 'en': regexes_en}

def keep_digit(s):
    return int(re.sub('[^0-9]', '', s))

def split_by_letters(contents, lang):
    item = REGEXES[lang].ITEM

    parts = re.split(f'({item})', contents, flags=re.MULTILINE)
    keys = [keep_digit(key) for key in parts[1::2]]
    values = parts[2::2]
    assert len(keys) == len(values)
    return zip(keys, values)

def letters_chunks(eng, heb):
    en = dict(split_by_letters(eng, 'en'))
    he = dict(split_by_letters(heb, 'he'))

    letters = list(sorted(set(en.keys()) | set(he.keys())))
    return [(letter, en.get(letter), he.get(letter)) for letter in letters]

def diff(eng, heb):
    letters = letters_chunks(eng, heb)
    print('<html><head><title>difftool</title></head><body>')

    for letter, en, he in letters:
        en_chunks = en.strip().split('\n') if en else ()
        he_chunks = he.strip().split('\n') if he else ()

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

    args = parser.parse_args()

    with open(args.english_file) as en, open(args.hebrew_file) as he:
        diff(en.read(), he.read())

if __name__ == "__main__":
    main()
