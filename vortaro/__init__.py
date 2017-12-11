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

from shlex import split
from os import environ, makedirs
from sys import stdin, stdout, stderr, exit
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

def ls(*from_langs, data_dir: Path=DATA,
       redis_host='localhost', redis_port: int=6379, redis_db: int=DB):
    '''
    List available dictionaries.

    :param from_langs: If you pass a languages, limit the listing to
        dictionaries from the passed language to other languages.
    :param pathlib.path data_dir: Vortaro data directory
    '''
    con = StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    for from_lang in sorted(from_langs or db.get_from_langs(con)):
        for to_lang in sorted(db.get_to_langs(con, from_lang)):
            stdout.write('%s -> %s\n' % (from_lang, to_lang))

def download(source: tuple(FORMATS), force=False, data_dir: Path=DATA,
             redis_host='localhost', redis_port: int=6379, redis_db: int=DB):
    '''
    Download a dictionary.

    :param source: Dictionary source to download from
    :param pathlib.path data_dir: Vortaro data directory
    :param bool force: Force updating of the index
    :param redis_host: Redis host
    :param redis_port: Redis port
    :param redis_db: Redis database number
    '''
    subdir = data_dir / source
    makedirs(subdir, exist_ok=True)
    FORMATS[source].download(subdir)

    con = StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    db.index(con, FORMATS, data_dir)

def index(drop=False, data_dir: Path=DATA,
          redis_host='localhost', redis_port: int=6379, redis_db: int=DB):
    '''
    Download a dictionary.

    :param pathlib.path data_dir: Vortaro data directory
    :param bool drop: Delete the existing index before indexing.
    :param redis_host: Redis host
    :param redis_port: Redis port
    :param redis_db: Redis database number
    '''
    con = StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    if drop:
        con.flushdb()
    db.index(con, FORMATS, data_dir)

def lookup(search: Word, limit: int=ROWS-2, *, width: int=COLUMNS,
           data_dir: Path=DATA,
           redis_host='localhost', redis_port: int=6379, redis_db: int=DB,
           from_langs: [str]=(), to_langs: [str]=()):
    '''
    Search for a word in the dictionaries, and format the result as a table.

    :param search: The word/fragment you are searching for
    :param limit: Maximum number of words to return
    :param width: Number of column in a line, or 0 to disable truncation
    :param from_langs: Languages the word is in, defaults to all
    :param to_langs: Languages to look for translations, defaults to all
    :param pathlib.Path data_dir: Vortaro data directory
    :param redis_host: Redis host
    :param redis_port: Redis port
    :param redis_db: Redis database number
    '''
    con = StrictRedis(host=redis_host, port=redis_port, db=redis_db)

    table = Table(search)
    for definition in db.search(con, search):
        if ((not from_langs) or (definition['from_lang'] in from_langs)) and \
                ((not to_langs) or (definition['to_lang'] in to_langs)):
            table.add(definition)
        if len(table) >= limit:
            break
    table.sort()

    if table:
        db.add_history(data_dir, search)
    for row in table.render(width, limit):
        stdout.write(row)
