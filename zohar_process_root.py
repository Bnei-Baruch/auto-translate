import requests
import re
import argparse
import tqdm
import sys

from zohar_download_article import download, MissingLanguage

SAMPLE_URL = 'https://kabbalahmedia.info/he/sources/yUcfylRm'
LINK_REGEX = re.compile(r'div id\=\"title\-[A-Za-z0-9]+\"')

def sources_list(base=SAMPLE_URL):
    LINK_REGEX = re.compile(r'div id\=\"title\-[A-Za-z0-9]+\"')
    
    src = requests.get(base).text
    links = LINK_REGEX.findall(src)
    
    return list({link[len('div id="title-'):-1] for link in links})

def guarded_download(src_dest):
    src, dest = src_dest
    try:
        download(src, dest)
    except MissingLanguage:
        pass
    except Exception as e:
        print('Failed downloading', src, file=sys.stderr)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=SAMPLE_URL, help="root tree url")
    parser.add_argument("--dest", default='zohar/', help="destination directory")
    parser.add_argument("--skip-process", dest='skip', action='store_true', help="skip processing (only download)")
    parser.add_argument("--no-skip-process", dest='skip', action='store_false', help="do not skip processing (default)")
    parser.set_defaults(skip=False)

    args = parser.parse_args()
    sources = sources_list(args.root)

    progress = tqdm.tqdm(range(len(sources)))
    for src, _ in zip(sources, progress):
        guarded_download((src, args.dest))

if __name__ == "__main__":
    main()
