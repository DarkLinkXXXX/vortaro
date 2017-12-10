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
from collections import OrderedDict
from shutil import get_terminal_size

from redis import StrictRedis

from .table import Table
from . import (
    db,
    dictcc, cedict, espdic
)
FORMATS = OrderedDict((
    ('dict.cc', dictcc),
    ('cc-cedict', cedict),
    ('espdic', espdic),
))
DB = 7 # Redis DB number

COLUMNS, ROWS = get_terminal_size((80, 20))
DATA = Path(environ.get('HOME', '.')) / '.vortaro'

def Word(x):
    illegal = set('\t\n\r')
    if set(x).issubset(illegal):
        raise ValueError('Word contains forbidden characters.')
    else:
        return x

def ls(*from_langs, data_dir: Path=DATA, index=False,
       redis_host='localhost', redis_port: int=6379, redis_db: int=DB):
    '''
    List available dictionaries.

    :param from_langs: If you pass a languages, limit the listing to
        dictionaries from the passed language to other languages.
    :param pathlib.path data_dir: Vortaro data directory
    :param bool index: Force updating of the index
    '''
    con = StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    db.index(con, FORMATS, data_dir, force=index)
    for from_lang in (from_langs or db.get_from_langs(con)):
        for to_lang in db.get_to_langs(con, from_lang):
            stdout.write('%s -> %s\n' % (from_lang, to_lang))

def download(source: tuple(FORMATS), data_dir: Path=DATA):
    '''
    Download a dictionary.

    :param source: Dictionary source to download from
    :param pathlib.path data_dir: Vortaro data directory
    '''
    subdir = data_dir / source
    makedirs(subdir, exist_ok=True)
    FORMATS[source].download(subdir)
    db.index(con, FORMATS, data_dir)

def lookup(search: Word, limit: int=ROWS-2, *, width: int=COLUMNS,
           index=False, data_dir: Path=DATA,
           redis_host='localhost', redis_port: int=6379, redis_db: int=DB,
           from_langs: [str]=(), to_langs: [str]=()):
    '''
    Search for a word in the dictionaries.

    :param search: The word/fragment you are searching for
    :param limit: Maximum number of words to return
    :param width: Number of column in a line, or 0 to disable truncation
    :param from_langs: Languages the word is in, defaults to all
    :param to_langs: Languages to look for translations, defaults to all
    :param pathlib.Path data_dir: Vortaro data directory
    :param bool index: Force updating of the index
    '''
    con = StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    db.index(con, FORMATS, data_dir, force=index)

    from_langs = set(from_langs)
    to_langs = set(to_langs)

    from_allowed = set(db.get_from_langs(con))
    for from_lang in from_langs:
        if from_lang in from_allowed:
            to_allowed = db.get_to_langs(con, from_lang)
            for to_lang in to_langs:
                if to_lang not in to_allowed:
                    tpl = 'Language pair not available: %s\n'
                    stderr.write(tpl % (from_lang, to_lang))
        else:
            stderr.write('Language not available: %s\n' % from_lang)

    con = StrictRedis(host=redis_host, port=redis_port, db=redis_db)

    table = Table(search)
    for definition in db.search(con, search):
        if (not from_langs or definition['from_lang'] in from_langs) and \
                (not to_langs or definition['to_lang'] in to_langs):
            table.add(definition)
    table.sort()

    if table:
        db.history(data_dir, search)
    for row in table.render(width, limit):
        stdout.write(row)
