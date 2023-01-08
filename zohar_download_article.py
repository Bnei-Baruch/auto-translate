import requests
import json
import lxml.html

import argparse
import os
from pathlib import Path
import shutil

# Base url of articles in different languages
SOURCE_BASE_URL = 'https://kabbalahmedia.info/{lang}/sources/'

# Part of the url which appears before article id
BEFORE_ID = 'sources/'

# Base url of the actual docx files
ASSET_BASE_URL = 'https://kabbalahmedia.info/assets/sources/'

# Sample url with tree links
SAMPLE_URL = 'https://kabbalahmedia.info/he/sources/yUcfylRm'

# Documents format
FORMAT = 'docx'


class HtmlFormatChanged(Exception):
    pass


class MissingLanguage(Exception):
    def __init__(self, article_id, lang):
        super().__init__(lang)
        self.article_id = article_id
        self.lang = lang


class NoArticleId(Exception):
    def __init__(self, url):
        super().__init__("Could not extract article id from url " + url)


class Asset:
    "Web page content and title"

    def __init__(self, content, filename, lang, local=False):
        self.content = content
        self.filename = filename
        self.lang = lang
        self.local = local

    def formatted_filename(self, _id):
        formatted = self.filename
        return f'{formatted}-{_id}'


def lang_links(txt):
    """This function extracts links per language part from a webpage.

    >>> js = 'var obj = {"data":{"he": "http://addr1", "en": "http://addr2"}};'
    >>> lang_links(js)
    '{"he": "http://addr1", "en": "http://addr2"}'
    """

    START_HINT = '"data":{'

    start = txt.find(START_HINT)
    if start < 0:
        raise HtmlFormatChanged("Data start hint not found")

    start += len(START_HINT)
    balance = 1
    for i in range(start, len(txt)):
        balance += (txt[i] == '{') - (txt[i] == '}')
        if balance == 0:
            return txt[start - 1:i + 1]

    raise HtmlFormatChanged("Unbalanced data section")


def load_assets(article_id, langs, fmt=FORMAT):
    "Downloads article with given id for given languages"

    assert langs, 'languages list cannot be empty'

    source_url = SOURCE_BASE_URL.format(lang=langs[0]) + article_id
    src = requests.get(source_url)

    links = json.loads(lang_links(src.text))
    filename = ''
    if langs[0] in links:
        filename = links[langs[0]]['docx']['name'].split('_')[-1][:-5]
    for lang in langs:
        if lang not in links:
            if not os.path.exists(f'zohar_{lang}/{filename}.docx'):
                raise MissingLanguage(article_id, lang)
            else:
                yield Asset('', filename, lang, True)
        else:
            filename = links[lang]['docx']['name'].split('_')[-1][:-5]
            url = ASSET_BASE_URL + article_id + '/' + links[lang][fmt]['name']
            yield Asset(requests.get(url).content, filename, lang)


def extract_id(asset_url):
    """Extracts document id from url.

    >>> extract_id('https://kabbalahmedia.info/he/sources/6WPLdxTX?language=en')
    '6WPLdxTX'
    """
    i = asset_url.find(BEFORE_ID)
    if i < 0:
        return NoArticleId(asset_url)

    return asset_url[i + len(BEFORE_ID):].split('?')[0]


def file_size(path):
    try:
        return Path(path).stat().st_size
    except FileNotFoundError:
        return -1


def download(_id, dest='', langs=None):
    if langs is None:
        langs = ['he']
    assets = list(load_assets(_id, langs=langs))

    assert assets, "documents number must be equal to LANGS length"

    folder = assets[0].formatted_filename(_id)
    base = os.path.join(dest, folder).replace("\"", "_")
    os.makedirs(base, exist_ok=True)

    paths = []
    filename = ''

    for asset in assets:
        path = os.path.join(base, asset.lang) + '.' + FORMAT
        paths.append((asset.lang, path))

        if asset.lang != 'he':  # if asset.lang == 'en':
            filename = asset.filename

        if not asset.local:
            with open(path, 'wb') as f:
                f.write(asset.content)
        else:
            shutil.copyfile(f'zohar_{asset.lang}/{filename}.docx', path)

    return paths, filename, base


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--source", default='he', help="source language")
    parser.add_argument("--target", default='en', help="target language")

    args = parser.parse_args()
    langs = (args.source, args.target)
    _id = extract_id(url)
    download(_id, langs)


if __name__ == "__main__":
    main()
