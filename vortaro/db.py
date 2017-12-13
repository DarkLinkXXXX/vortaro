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

import datetime
from os import makedirs
from sys import stderr
from hashlib import md5
from collections import defaultdict

from . import transliterate

LOG_INTERVAL = 10000
MAX_PHRASE_LENGTH = 18

def add_history(data, search):
    with (data / 'history').open('a') as fp:
        fp.write('%s\t%s\n' % (search, datetime.datetime.now()))
def get_history(data):
    with (data / 'history').open('r') as fp:
        for line in fp:
            yield line.split('\t', 1)[0]

def _get_out_of_date(con, path):
    file_mtime = int(path.stat().st_mtime) # buffer against rounding errors
    db_mtime_str = con.get('dictionaries:%s' % path.absolute())
    return (not db_mtime_str) or \
        file_mtime > int(db_mtime_str.decode('ascii').split('.')[0])
def _set_up_to_date(con, path):
    con.set('dictionaries:%s' % path.absolute(), path.stat().st_mtime)
def _set_out_of_date(con, path):
    con.delete('dictionaries:%s' % path.absolute())

def languages(con):
    for l in con.sscan_iter(b'languages'):
        yield l.decode('ascii')

def search(con, from_langs, query):
    if not from_langs:
        from_langs = tuple(languages(con))

    sub_queries = defaultdict(set)
    for alphabet in transliterate.alphabets:
        t = alphabet.from_roman(query)
        for i in range(len(t), MAX_PHRASE_LENGTH+1):
            sub_queries[i].add(t.encode('utf-8'))

    if sub_queries:
        for i in range(min(sub_queries), MAX_PHRASE_LENGTH+1):
            for a in sub_queries[i]:
                for language in from_langs:
                    key = b'lengths:%s:%d' % (language.encode('ascii'), i)
                    for b in con.sscan_iter(key):
                        if a in b:
                            for c in con.sscan_iter(b'phrase:%s' % b):
                                yield _line_loads(c)

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
                    key = (
                        line['from_lang'].encode('ascii'),
                        min(MAX_PHRASE_LENGTH, len(phrase)),
                    )
                    phrases[key].add(phrase)
                    con.sadd('phrase:%s' % phrase, _line_dumps(line))
                for key, values in phrases.items():
                    con.sadd(b'lengths:%s:%d' % key, *values)
                stderr.write('Processed %s\n' % file)
    for fullkey in con.keys(b'lengths:*'):
        _, lang, _ = fullkey.split(b':')
        con.sadd(b'languages', lang)

def _line_dumps(x):
    return '\t'.join((
        x.get('part_of_speech', ''),
        x['from_word'], x['from_lang'],
        x['to_word'], x['to_lang'],
    )).encode('utf-8')
def _line_loads(x):
    y = {}
    y['part_of_speech'], y['from_word'], y['from_lang'], \
        y['to_word'], y['to_lang'] = x.decode('utf-8').split('\t')
    return y
