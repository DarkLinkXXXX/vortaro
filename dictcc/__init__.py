from sys import stdout

from . import dictionaries
from .lines import Line, Table

def ls(*languages):
    '''
    List available dictionaries.

    :param languages: If you pass any languages, limit the listing to
        dictionaries from the passed languages to other languages.
    '''
    for pair in dictionaries.ls(languages or None):
        stdout.write('%s -> %s\n' % pair)

def download():
    '''
    Download a dictionary.
    '''
    import webbrowser
    stdout.write('''\
The download page will open in a web browser. Download the dictionary
of interest (as zipped text), unzip it, and save the text file as this:
~/.dict.cc/[from language]-[to language].txt

Press enter when you are ready.
''')
    input()
    webbrowser.open('https://www1.dict.cc/translation_file_request.php?l=e')

def look_up(search, from_langs: [str]=(), to_langs: [str]=()):
    '''
    Search for a word in the dictionaries.

    :param search: The word/fragment you are searching for
    :param from_langs: Languages the word is in, defaults to all
    :param to_langs: Languages to look for translations, defaults to all
    '''
    from itertools import product

    if from_langs and to_langs:
        pairs = product(from_langs, to_langs)
    elif from_langs:
        pairs = dictionaries.ls(from_langs)
    elif to_langs:
        pairs = product(dictionaries.from_langs(), to_langs)
    else:
        pairs = dictionaries.ls()

    table = Table(search)
    for from_lang, to_lang in pairs:
        fp = dictionaries.open(from_lang, to_lang)
        if fp:
            for rawline in fp:
                if not (rawline.startswith('#') or not rawline.strip()):
                    from_word, to_word, pos = rawline.rstrip('\n').split('\t')
                    line = Line(from_lang, from_word, to_lang, to_word, pos)
                    if search in line.from_word:
                        table.append(line)
            fp.close()
    stdout.write(str(table))
