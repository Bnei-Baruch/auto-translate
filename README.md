# Zohar Files Scrapping Tool

## User Guide

### Installation 

  1. Download the latest release from this repository, enter the directory containing it.
  2. Install pip requirements:

```shell
pip3 install -r requirements.txt
```

### Usage

The scrapping tool contains three major scripts:
  * zohar_download_article.py
  * zohar_preprocess_file.py
  * zohar_split_heuristic.py
  * zohar_create_summary.py
  * zohar_process_root.py
  
To check the exact paramters of every script run:
```shell
python3 {script_name} --help
```

#### zohar_download_article.py

This script gets a link to an article on kabbalahmedia.info website, 
downloads docx files of the article in Hebew and English and saves them in
a directory named by article title and id.

#### zohar_preprocess_article.py

This script receives the paths of the two files downloaded by zohar_download_article.py and converts them
to clear text files using the following rules:

  * By default all paragraphs are put on new lines and all other newlines are removed.
  * There is an optional *chunk* argument, which allows to split the text not only by paragraphs but also by sentences and characters or not to split at all.
  * The number of characters taken when chunk option equals 'characters' is passed as an argument.
  * When chunk option equals 'sentences' the sentences boundaries are determined by predefined regular expressions located in regex_{lang}.py file.
  * When chunk option is 'joined' all paragraphs in the same Ot are joined.
  * After the initial clear text content is created it is altered using regular expressions describing language specific replace directives.
    These regular expressions are also defined in regex_{lang}.py.
  
### zohar_split_heuristic.py

This script gets english and hebrew text files and the maximum number of words per english text entry and outputs new pair of files (or overrides existsing files). Every Ot in the output is split so that the length of every chunk inside does not diverge too much from the requested number of words.

### zohar_create_summary.py

This script gets english and hebrew text files and creates html file for every letter in the input containing chunking summary. 
  
#### zohar_process_root.py
  This script runs zohar_download_article.py, zohar_preprocess_article.py, zohar_split_heuristic.py and zohar_create_summary.py on all links contained in the article tree on kabbalahmedia.info website.

### Regexes
  Language related regexes are located in a file `regexes_{lang}.py` file where `{lang}` can be either `he` or `en`. Every language regex file must define the following constants:
  
  <dl>
    <dt>ITEM</dt>
    <dd>Beggining of a new item (אות)</dd>
    <dt>SENTENCES_SPLIT</dt>
    <dd>List of regexes that split the sentences (used when chunk='sentences').</dd>
    <dt>SENTENCES_KEEP</dt>
    <dd>List of regexes that prevent the sentence from being split  (used when chunk='sentences', has precedence over SENTENCES_SPLIT).</dd>
    <dt>REPLACE</dt>
    <dd>Replacement regexes (pairs of items: regex pattern and a replacement string)
    <dt>HIGHLIGHT</dt>
    <dd>Hightlighted text regexes (the highlighted text can be optionally added to the comments in the summary html)
   </dl>
