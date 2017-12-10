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

import re
import pickle
from sys import stdout
from collections import defaultdict, namedtuple, OrderedDict

from . import (
    db, alphabets,
    dictcc, cedict, espdic,
) 

FORMATS = OrderedDict((
    ('dict.cc', dictcc),
    ('cc-cedict', cedict),
    ('espdic', espdic),
))

Dictionary = namedtuple('Dictionary', ('format', 'path', 'reverse'))

def update_word_index(i, languages, pairs):
    change = False
    for pair in pairs:
        from_lang, to_lang = pair
        if pair not in i:
            i[pair] = {}
        print(pair)
        for d in languages.get(from_lang, {}).get(to_lang):
            if d.path not in i:
                i[pair][d.path] = []
                change = True
                from_roman = getattr(alphabets, from_lang, alphabets.identity).from_roman

                for line in FORMATS[d.format].read(d.path):
                    line.reverse = d.reverse
                    search_trans = from_roman(line.from_word).encode('utf-8')
                    i[pair][d.path].append((search_trans, pickle.dumps(line)))
    return change

def file_index(data):
    '''
    Load the dictionary language index, rebuilding it if necessary.

    :param pathlib.Path data: Path to the data directory
    '''
    i = db.file_index(data)
    mtimes = tuple(map(_mtime, _find(data)))
    if mtimes:
        if (not i.exists()) or (max(mtimes) > _mtime(i)):
            languages = _file_index(data)
            with i.open('wb') as fp:
                pickle.dump(languages, fp)
        else:
            with i.open('rb') as fp:
                languages = pickle.load(fp)
    else:
        languages = {}
    return languages

def _file_index(data):
    '''
    Build the dictionary language index.

    :param pathlib.Path data: Path to the data directory
    '''
    languages = defaultdict(lambda: defaultdict(list))
    for name, module in FORMATS.items():
        directory = data / name
        if directory.is_dir():
            for file in directory.iterdir():
                pair = module.index(file)
                if pair:
                    f, t = pair
                    languages[f][t].append(Dictionary(name, file, False))
                    languages[t][f].append(Dictionary(name, file, True))

    # Convert to normal dict for pickling.
    i = {k: dict(v) for k,v in languages.items()}
    for f in i:
        for t in i[f]:
            i[f][t].sort(key=lambda d: d.path.stat().st_size, reverse=True)
    return i

def ls(languages, froms):
    for from_lang in sorted(froms if froms else from_langs(languages)):
        for to_lang in sorted(to_langs(languages, from_lang)):
            yield from_lang, to_lang

def from_langs(languages):
    return set(languages)

def to_langs(languages, from_lang):
    return set(languages.get(from_lang, set()))

def _mtime(path):
    return path.stat().st_mtime

def _find(data):
    for name, _ in FORMATS.items():
        directory = data / name
        if directory.is_dir():
            for file in directory.iterdir():
                yield file
