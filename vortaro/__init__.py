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

from .render import Table, Stream
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

def languages(redis_host='localhost', redis_port: int=6379, redis_db: int=DB):
    '''
    List from-languages that have been indexed.

    :param redis_host: Redis host
    :param redis_port: Redis port
    :param redis_db: Redis database number
    '''
    con = StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    for language in db.languages(con):
        print(language)

def stream(search: Word, limit: int=ROWS-2, *, width: int=COLUMNS,
           data_dir: Path=DATA,
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
    :param redis_host: Redis host
    :param redis_port: Redis port
    :param redis_db: Redis database number
    '''
    con = StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    fmt = partial(Stream, search, width)

    i = 0
    for definition in db.search(con, from_langs, to_langs, search):
        i += 1
        stdout.write(fmt(definition))
        if i >= limit:
            break
    if i:
        db.add_history(data_dir, search)

def table(search: Word, limit: int=ROWS-2, *, width: int=COLUMNS,
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

    t = Table(search)
    for definition in db.search(con, from_langs, to_langs, search):
        t.add(definition)
        if len(t) >= limit:
            break
    t.sort()

    if t:
        db.add_history(data_dir, search)
    for row in t.render(width, limit):
        stdout.write(row)
