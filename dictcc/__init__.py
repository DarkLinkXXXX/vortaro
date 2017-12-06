# Tom's dict.cc dictionary reader
# Copyright (C) 2017  Thomas Levine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from sys import stdout
from shutil import get_terminal_size

from . import dictionaries
from .lines import Line, Table

COLUMNS, ROWS = get_terminal_size((80, 20))

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
    import textwrap
    import webbrowser
    directions = '''\
The download page will open in a web browser. Download the dictionary
of interest (as zipped text), unzip it, and put the text file inside this
directory: ~/.dict.cc/'''
    for line in textwrap.wrap(directions, COLUMNS):
        stdout.write(line + '\n')
    stdout.write('\n')
    stdout.write('Press enter when you are ready.\n')
    input()
    webbrowser.open('https://www1.dict.cc/translation_file_request.php?l=e')

def lookup(search, limit: int=ROWS-2, *,
           width: int=COLUMNS,
           from_langs: [tuple(dictionaries.LANGUAGES)]=(),
           to_langs: [tuple(dictionaries.LANGUAGES)]=()):
    '''
    Search for a word in the dictionaries.

    :param search: The word/fragment you are searching for
    :param limit: Maximum number of words to return
    :param width: Number of column in a line, or 0 to disable truncation
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
        d = dictionaries.open(from_lang, to_lang)
        if d:
            with d.path.open() as fp:
                for rawline in fp:
                    if not (rawline.startswith('#') or not rawline.strip()):
                        left_word, right_word, pos = rawline.rstrip('\n').split('\t')
                        if d.reversed:
                            to_word, _from_word = left_word, right_word
                        else:
                            _from_word, to_word = left_word, right_word
                        from_word = _from_word.split('[', 1)[0].rstrip()
                        line = Line(pos, from_lang, from_word, to_lang, to_word)
                        if search in from_word:
                            table.append(line)
    table.sort()
    for row in table.render(width, limit):
        stdout.write(row)
