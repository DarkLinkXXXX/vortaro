def download():
    '''
    Download a dictionary.
    '''
    import sys, webbrowser
    sys.stdout.write('''\
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

    from . import dictionaries
    from .lines import Line, Table

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
                line = Line(rawline.rstrip('\n').split('\t'))
                if search in line.from_word:
                    table.append(line)
            fp.close()
    return table
