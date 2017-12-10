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
N = 3 # Fragment size

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

def search(con, x):
    root = x.lower()
    if set(root).issubset(transliterate.full_alphabet):
        tpl = 'fragment:%s'
        keys = tuple(tpl % f for f in set(_search_fragments(root)))
        if len(keys) == 1:
            key = tuple(keys)[0]
        else:
            key = 'tmp:phrases'
            con.zinterstore(key, keys, 'min')
        for phrase, _ in con.zscan_iter(key):
            if root in phrase.decode('utf-8'):
                yield from map(pickle.loads, con.hvals(b'phrase:%s' % phrase))

def index(con, formats, data, force=False):
    '''
    Build the dictionary language index.

    :param pathlib.Path data: Path to the data directory
    '''
    if force:
        for name, module in formats.items():
            directory = data / name
            if directory.is_dir():
                for file in directory.iterdir():
                    _set_out_of_date(con, file)

    skip = 0
    files = 0
    definitions = 0
    pairs = set()
    fragments = defaultdict(list)
    for name, module in formats.items():
        directory = data / name
        if not directory.is_dir():
            continue
        for file in directory.iterdir():
            if not _get_out_of_date(con, file):
                continue
            files += 1
            for line in module.read(file):
                phrase = _restrict_chars(line['from_lang'], line.pop('search_phrase'))
                for fragment in set(_index_fragments(phrase)):
                    fragments[fragment].append(phrase)
                xs = (
                    line['from_lang'], line['from_word'],
                    line['to_lang'], line['to_word'],
                )
                identifier = md5('\n'.join(xs).encode('utf-8')).hexdigest()
                pairs.add((line['from_lang'], line['to_lang']))
                con.hset('phrase:%s' % phrase, identifier, pickle.dumps(line))

                definitions += 1
                if definitions % LOG_INTERVAL == 0:
                    for fragment, phrases in fragments.items():
                        def scored():
                            for phrase in set(phrases):
                                yield len(phrase) 
                                yield phrase
                        con.zadd('fragment:%s' % fragment, *scored())
                    
                    for pair in pairs:
                        _add_pair(con, *pair)
                    pairs.clear()

                    msg = '\rIndexed %d definitions from %d files (Skipped %d already-indexed files)'
                    stderr.write(msg % (definitions, files, skip))
                    
            _set_up_to_date(con, file)
        else:
            skip += 1

def _restrict_chars(lang, text):
    return getattr(transliterate, lang, transliterate.identity).to_roman(text).lower()

def _search_fragments(search):
    if len(search) <= N:
        yield search
    else:
        for i in range(1+len(search)-N):
            yield search[i:i+N]

def _index_fragments(phrase):
    for i in range(len(phrase)):
        for j in range(1, 1+N):
            yield phrase[i:i+j]
