## Item (letter) indicator
ITEM = r'^\.[0-9]+'

## Chunk Regexes

# The sentences are not split in the following points (it overrides _SPLIT items)
SENTENCES_KEEP = [r'\.\"', ITEM]

# The sentences are split in the following points
SENTENCES_SPLIT = [r'\.']

## Replace Regexes
REPLACE = []

## Select regexes (to be selected in the final html)
HIGHLIGHT = ['ג"ע']
