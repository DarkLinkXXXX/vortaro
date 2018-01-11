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
from itertools import product
from collections import defaultdict

from .transliterate import ALPHABETS, IDENTITY

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
    for l in con.sscan_iter(b'pairs'):
        yield tuple(l.decode('ascii').split(':'))

def search(con, from_langs, to_langs, query):
    if not from_langs or not to_langs:
        ls = tuple(languages(con))
        if not from_langs:
            from_langs = sorted(set(l[0] for l in ls))
        if not to_langs:
            to_langs = sorted(set(l[1] for l in ls))
    pairs = tuple(product(from_langs, to_langs))

    start = min(len(alphabet.from_roman(query)) \
                for alphabet in ALPHABETS.values())
    encoded_queries = {}
    for i in range(start, MAX_PHRASE_LENGTH+1):
        results = []
        for from_lang, to_lang in pairs:
            if from_lang in encoded_queries:
                encoded_query = encoded_queries[from_lang]
            else:
                alphabet = ALPHABETS.get(from_lang, IDENTITY)
                encoded_query = alphabet.from_roman(query).encode('utf-8')
                encoded_queries[from_lang] = encoded_query
            lang_key = (from_lang.encode('ascii'), to_lang.encode('ascii'))
            key = b'lengths:%s:%s:%d' % (lang_key + (i,))
            for word_fragment in con.sscan_iter(key):
                if encoded_query in word_fragment:
                    key = b'phrase:%s:%s:%s' % (lang_key + (word_fragment,))
                    for definition in con.sscan_iter(key):
                        results.append(_line_loads(definition))
        yield from sorted(results, key=lambda line: line['to_word'])

def index(con, formats, data):
    '''
    Build the dictionary language index.

    :param pathlib.Path data: Path to the data directory
    '''
    processed = set(x.decode('utf-8') for x in con.sscan_iter(b'processed'))
    for name, module in formats.items():
        directory = data / name
        if directory.is_dir():
            for file in directory.iterdir():
                if str(file.absolute()) in processed:
                    continue
                lines = tuple(module.read(file))
                phrases = defaultdict(set)
                pairs = set()
                for line in lines:
                    line['from_lang'] = line['from_lang'].lower()
                    line['to_lang'] = line['to_lang'].lower()
                    phrase = line.pop('search_phrase').lower()
                    key = (
                        line['from_lang'].encode('ascii'),
                        line['to_lang'].encode('ascii'),
                        min(MAX_PHRASE_LENGTH, len(phrase)),
                    )
                    phrases[key].add(phrase)
                    args = key[:2] + (phrase.encode('utf-8'),)
                    con.sadd(b'phrase:%s:%s:%s' % args, _line_dumps(line))
                for key, values in phrases.items():
                    con.sadd(b'lengths:%s:%s:%d' % key, *values)
                stderr.write('Processed %s\n' % file)
                con.sadd(b'processed', str(file.absolute()))
    for fullkey in con.keys(b'lengths:*'):
        _, from_lang, to_lang, _ = fullkey.split(b':')
        con.sadd(b'pairs', b'%s:%s' % (from_lang, to_lang))

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
