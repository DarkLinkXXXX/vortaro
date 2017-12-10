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

import datetime, pickle
from os import makedirs
from hashlib import md5
from itertools import product, permutations, combinations

from . import to_roman

N = 3 # Fragment size

def history(data, search):
    with (data / 'history').open('a') as fp:
        fp.write('%s\t%s\n' % (search, datetime.datetime.now()))

def _get_up_to_date(con, path):
    file_mtime = 1 + int(path.stat().st_mtime) # buffer against rounding errors
    db_mtime_str = con.get('dictionaries:%s' % path.absolute())
    return (not db_mtime_str) or \
        file_mtime > int(db_mtime_str.decode('ascii').split('.')[0])
def _set_up_to_date(con, path):
    con.set('dictionaries:%s' % path.absolute(), path.stat().st_mtime)

def get_from_langs(con):
    for key in con.sscan_iter('languages:*'):
        _, from_lang = key.decode('ascii').split(':')
        yield from_lang
def get_to_langs(con, from_lang):
    return con.sscan_iter('languages:%s' % from_lang)
def _add_pair(con, from_lang, to_lang):
    con.sadd('languages:%s' % from_lang, to_lang)
    con.sadd('languages:%s' % to_lang, from_lang)

def search(con, x):
    full_alphabet = b''.join(con.sscan_iter('characters')).decode('utf-8')
    y = x.lower()

    if set(y).issubset(full_alphabet):
        tpl = 'fragment:%s'
        if len(y) >= N:
            phrases = con.sinter(tpl % f for f in set(_smaller_fragments(y)))
        else:
            phrases = con.sunion(tpl % f for f in \
                                 set(_bigger_fragments(full_alphabet, y)))
        for phrase in phrases:
            if y in phrase.decode('utf-8'):
                yield from map(pickle.loads, con.hvals(b'phrase:%s' % phrase))

def index(con, formats, data, force=False):
    '''
    Build the dictionary language index.

    :param pathlib.Path data: Path to the data directory
    '''
    for name, module in formats.items():
        directory = data / name
        if directory.is_dir():
            for file in directory.iterdir():
                if force or not _get_up_to_date(con, file):
                    for line in module.read(file):
                        _index_line(con, line)
                    _set_up_to_date(con, file)

def _restrict_chars(x):
    return getattr(to_roman, x, to_roman.identity)(x).lower()

def _index_line(con, line):
    phrase = _restrict_chars(line.pop('search_phrase'))

    for character in phrase:
        con.sadd('characters', character)
    for fragment in set(_smaller_fragments(phrase)):
        con.sadd('fragment:%s' % fragment, phrase)

    xs = (
        line['from_lang'], line['from_word'],
        line['to_lang'], line['to_word'],
    )
    identifier = md5('\n'.join(xs).encode('utf-8')).hexdigest()
    con.hset('phrase:%s' % phrase, identifier, pickle.dumps(line))

def _bigger_fragments(full_alphabet, search):
    '''
    Add to the right to make more fragments.
    '''
    for options in combinations(full_alphabet, N - len(search)):
        for suffix in permutations(options):
            yield search + ''.join(suffix)

def _smaller_fragments(phrase):
    if len(phrase) >= N:
        yield phrase
    else:
        columns = []
        for i in range(len(phrase)):
            columns.append(phrase[i:i+1-N])
        for letters in zip(*columns):
            yield ''.join(letters)
