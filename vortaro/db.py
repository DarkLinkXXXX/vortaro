# vortaro
# Copyright (C) 2017  Thomas Levine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime, pickle
from os import makedirs
from sys import stderr
from hashlib import md5
from collections import defaultdict

from . import transliterate

LOG_INTERVAL = 10000
MAX_PHRASE_LENGTH = 12

def history(data, search):
    with (data / 'history').open('a') as fp:
        fp.write('%s\t%s\n' % (search, datetime.datetime.now()))

def _get_out_of_date(con, path):
    file_mtime = int(path.stat().st_mtime) # buffer against rounding errors
    db_mtime_str = con.get('dictionaries:%s' % path.absolute())
    return (not db_mtime_str) or \
        file_mtime > int(db_mtime_str.decode('ascii').split('.')[0])
def _set_up_to_date(con, path):
    con.set('dictionaries:%s' % path.absolute(), path.stat().st_mtime)
def _set_out_of_date(con, path):
    con.delete('dictionaries:%s' % path.absolute())

def get_from_langs(con):
    for key in con.scan_iter('languages:*'):
        _, from_lang = key.decode('ascii').split(':')
        yield from_lang
def get_to_langs(con, from_lang):
    for member in con.sscan_iter('languages:%s' % from_lang):
        yield member.decode('ascii')
def _add_pair(con, from_lang, to_lang):
    con.sadd('languages:%s' % from_lang, to_lang)
    con.sadd('languages:%s' % to_lang, from_lang)

def search(con, query):
    sub_queries = defaultdict(set)
    for alphabet in transliterate.alphabets:
        t = alphabet.from_roman(query)
        sub_queries[len(t)].add(t)

    for i in range(min(sub_queries), MAX_PHRASE_LENGTH+1):
        for x in sub_queries[i]:
            for y in con.sscan_iter(b'lengths:%d' % i, match='*%s*' % x):
                for z in con.lscan_iter('phrase:%s' % y):
                    yield pickle.loads(z)

def index(con, formats, data):
    '''
    Build the dictionary language index.

    :param pathlib.Path data: Path to the data directory
    '''
    for name, module in formats.items():
        directory = data / name
        if directory.is_dir():
            for file in directory.iterdir():
                lines = tuple(module.read(file))
                phrases = defaultdict(set)
                pairs = set()
                for line in lines:
                    line['from_lang'] = line['from_lang'].lower()
                    line['to_lang'] = line['to_lang'].lower()
                    phrase = line.pop('search_phrase').lower()
                    phrases[len(phrase)].add(phrase)
                    pairs.add((line['from_lang'], line['to_lang']))
                    con.lpush('phrase:%s' % phrase, pickle.dumps(line))
                for key, values in phrases.items():
                    con.sadd(b'lengths:%d' % key, *values)
                for pair in pairs:
                    _add_pair(con, *pair)
                stderr.write('Processed %s' % file)
