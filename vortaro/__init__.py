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

from os import environ, makedirs
from sys import stdout, stderr, exit
from pathlib import Path
from itertools import product
from functools import partial
from shutil import get_terminal_size

from . import dictionaries
from .lines import Table
from .db import DATA, history

COLUMNS, ROWS = get_terminal_size((80, 20))
DATA = Path(environ.get('HOME', '.')) / '.vortaro'

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
    i = dictionaries.file_index(data_dir)
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

def lookup(search: Word, limit: int=ROWS-2, *, width: int=COLUMNS,
           force=False, data_dir: Path=DATA,
           redis_host='localhost', redis_port: int=6379, redis_db: int=0,
           from_langs: [str]=(), to_langs: [str]=()):
    '''
    Search for a word in the dictionaries.

    :param search: The word/fragment you are searching for
    :param limit: Maximum number of words to return
    :param width: Number of column in a line, or 0 to disable truncation
    :param from_langs: Languages the word is in, defaults to all
    :param to_langs: Languages to look for translations, defaults to all
    :param pathlib.Path data_dir: Vortaro data directory
    :param bool force: Force updating of the caches
    '''
    languages = dictionaries.file_index(data_dir)

    not_available = set(from_langs).union(to_langs) - set(languages)
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
    pairs = tuple(pairs)

    con = StrictRedis(host=redis_host, port=redis_port, db=redis_db)

    table = Table(search)
    for key in db.search(con, search):
        table.add(db.definition(con, key))
    table.sort()

    if table:
        db.history(data_dir, search)
    for row in table.render(width, limit):
        stdout.write(row)
