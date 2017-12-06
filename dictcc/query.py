from collections import namedtuple
from itertools import product

from . import dictionaries

'\033[4m'

def query(search, from_langs: [str]=(), to_langs: [str]=()):
    '''
    :param search: The word/fragment you are searching for
    :param from_langs: Languages the word is in, defaults to all
    :param to_langs: Languages to look for translations, defaults to all
    '''
    if from_langs and to_langs:
        pairs = product(from_langs, to_langs)
    elif from_langs:
        pairs = dictionaries.ls(from_langs)
    elif to_langs:
        pairs = product(dictionaries.from_langs(), to_langs)
    else:
        pairs = dictionaries.ls()

    lines = []
    cw = column_widths.new()
    for from_lang, to_lang in pairs:
        fp = dictionaries.open(from_lang, to_lang)
        if fp:
            for rawline in fp:
                line = Line(rawline.rstrip('\n').split('\t'))
                if search in line.from_word:
                    lines.append(line)
                    column_widths.update(cw, line)
            fp.close()
    
Line = namedtuple('Line', ('from_word', 'to_word', 'part_of_speech'))

class column_widths(object):
    @staticmethod
    def new():
        return [0, 0, 0]
    @staticmethod
    def update(columns, line):
        for i, text in enumerate(line):
            columns[i] = max(columns[i], len(text))
