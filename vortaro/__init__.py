# vortaro
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

import datetime
from os import makedirs
from sys import stdout, stderr, exit
from pathlib import Path
from functools import partial
from shutil import get_terminal_size

from . import alphabets, dictionaries
from .lines import Table
from .paths import DATA, history

COLUMNS, ROWS = get_terminal_size((80, 20))

def Word(x):
    illegal = set('\t\n\r')
    if set(x).issubset(illegal):
        raise ValueError('Word contains forbidden characters.')
    else:
        return x

def ls(*languages, data_dir: Path=DATA):
    '''
    List available dictionaries.

    :param languages: If you pass any languages, limit the listing to
        dictionaries from the passed languages to other languages.
    :param pathlib.path data_dir: Vortaro data directory
    '''
    i = dictionaries.index(data_dir)
    for pair in dictionaries.ls(i, languages or None):
        stdout.write('%s -> %s\n' % pair)

def download(source: tuple(dictionaries.FORMATS), data_dir: Path=DATA):
    '''
    Download a dictionary.

    :param source: Dictionary source to download from
    :param pathlib.path data_dir: Vortaro data directory
    '''
    subdir = data_dir / source
    makedirs(subdir, exist_ok=True)
    dictionaries.FORMATS[source].download(subdir)

def lookup(search: Word, limit: int=ROWS-2, *,
           data_dir: Path=DATA,
           width: int=COLUMNS,
           from_langs: [str]=(),
           to_langs: [str]=()):
    '''
    Search for a word in the dictionaries.

    :param search: The word/fragment you are searching for
    :param limit: Maximum number of words to return
    :param width: Number of column in a line, or 0 to disable truncation
    :param from_langs: Languages the word is in, defaults to all
    :param to_langs: Languages to look for translations, defaults to all
    :param pathlib.Path data_dir: Vortaro data directory
    '''
    from itertools import product
    languages = dictionaries.index(data_dir)

    not_available = set(languages).difference(from_langs).difference(to_langs)
    if not_available:
        msg = 'These languages are not available: %s\n'
        stderr.write(msg % ', '.join(sorted(not_available)))
        exit(1)

    if from_langs and to_langs:
        pairs = product(from_langs, to_langs)
    elif from_langs:
        pairs = dictionaries.ls(languages, from_langs)
    elif to_langs:
        pairs = product(dictionaries.from_langs(languages), to_langs)
    else:
        pairs = dictionaries.ls(languages, None)

    table = Table(search)
    for from_lang, to_lang in pairs:
        from_roman = getattr(alphabets, from_lang, alphabets.identity).from_roman
        search_trans = from_roman(search)
        for line in dictionaries.read(languages, from_lang, to_lang):
            if search_trans in line.from_word:
                table.append(line)
    table.sort()
    if table:
        with history(data_dir).open('a') as fp:
            fp.write('%s\t%s\n' % (search, datetime.datetime.now()))
    for row in table.render(width, limit):
        stdout.write(row)