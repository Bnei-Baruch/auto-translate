import requests
import json
import lxml.html

import argparse
import os
from pathlib import Path

# Base url of articles in different languages
SOURCE_BASE_URL = 'https://kabbalahmedia.info/{lang}/sources/'

# Part of the url which appears before article id
BEFORE_ID = 'sources/'

# Base url of the actual docx files
ASSET_BASE_URL = 'https://kabbalahmedia.info/assets/sources/'

# Sample url with tree links
SAMPLE_URL = 'https://kabbalahmedia.info/he/sources/yUcfylRm'

# The documents in these languages will be downloaded:
LANGS = ('en', 'he')

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

    def __init__(self, content, title, lang):
        self.content = content
        self.title = title
        self.lang = lang

    def formatted_title(self, _id):
        formatted = self.title.split('|')[0].split('-')[0].strip().replace(' ', '-')
        return f'{formatted}-{_id}'
        
def lang_links(txt):
    """This function extracts links per language part from a webpage.

    >>> js = 'var obj = {"data":{"he": "http://addr1", "en": "http://addr2"}};'
    >>> lang_detals(obj)
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
    
    raise HtmlFormatChanged("Unblanced data section")

def load_assets(article_id, langs=LANGS, fmt=FORMAT):
    "Downloads article with given id for given languages"

    assert langs, 'languages list cannot be empty'

    source_url = SOURCE_BASE_URL.format(lang=langs[0]) + article_id
    src = requests.get(source_url)
    title = lxml.html.fromstring(src.text).findtext('.//title')
    
    links = json.loads(lang_links(src.text))
    for lang in langs:
        if lang not in links:
            raise MissingLanguage(article_id, lang)
    
        url = ASSET_BASE_URL + article_id + '/' + links[lang][fmt]
        yield Asset(requests.get(url).content, title, lang)

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

def download(_id, dest=''):
    assets = list(load_assets(_id))

    assert assets, "documents number must be equal to LANGS length"

    folder = assets[0].formatted_title(_id)
    base = os.path.join(dest, folder)
    os.makedirs(base, exist_ok=True)

    paths = []
    title = ''
    
    for asset in assets:
        path = os.path.join(base, asset.lang) + '.' + FORMAT
        paths.append((asset.lang, path))

        if asset.lang == 'en':
            title = asset.title

        if file_size(path) == len(asset.content):
            continue

        with open(path, 'wb') as f:
            f.write(asset.content)

    return paths, title, base

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")

    args = parser.parse_args()
 
    _id = extract_id(url)
    download(_id)

if __name__ == "__main__":
    main()
