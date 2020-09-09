# Zohar Files Scrapping Tool

## User guide

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
  * zohar_process_root.py

#### zohar_download_article.py

This script gets a link to an article on kabbalahmedia.info website, 
downloads docx files of the article in Hebew and English and saves them in
a directory named by article title and id.

#### zohar_preprocess_article.py

This script receives the paths of the two files downloaded by zohar_download_article.py and converts them
to clear text files using the following rules:

  * By default all paragraphs are put on new lines and all other newlines are removed.
  * There is an optional *chunk* argument, which allows to split the text not only by paraphs but also by sentences and characters.
  * The number of characters taken when chunk option equals 'characters' is passed as an argument.
  * When chunk option equals 'sentences' the sentences boundaries are determined by predefined regular expressions located in regex_{lang}.py file.
  * After the initial clear text content is created it is altered using regular expressions describing language specific replace directives.
    These regular expressions are also defined in regex_{lang}.py.
  * Creates html file for every input file containing chunking summary.
  
#### zohar_process_root.py
  This script runs zohar_download_article.py and then zohar_preprocess_article.py on all links contained in the article tree on kabbalahmedia.info website
