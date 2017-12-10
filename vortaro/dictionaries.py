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

from .lines import Line
from . import paths, dictcc, cedict, espdic

FORMATS = OrderedDict((
    ('dict.cc', dictcc),
    ('cc-cedict', cedict),
    ('espdic', espdic),
))

Dictionary = namedtuple('Dictionary', ('format', 'path', 'reversed'))

def index(data):
    '''
    Load the dictionary language index, rebuilding it if necessary.

    :param pathlib.Path data: Path to the data directory
    '''
    i = paths.index(data)
    mtimes = tuple(map(_mtime, _find(data)))
    if mtimes:
        if (not i.exists()) or (max(mtimes) > _mtime(i)):
            languages = _index(data)
            with i.open('wb') as fp:
                pickle.dump(languages, fp)
        else:
            with i.open('rb') as fp:
                languages = pickle.load(fp)
    else:
        languages = {}
    return languages

def _index(data):
    '''
    Build the dictionary language index.

    :param pathlib.Path data: Path to the data directory
    '''
    languages = defaultdict(dict)
    for name, module in FORMATS.items():
        directory = data / name
        if directory.is_dir():
            for file in directory.iterdir():
                pair = module.index(file)
                if pair:
                    f, t = pair
                    languages[f][t] = Dictionary(name, file, False)
                    languages[t][f] = Dictionary(name, file, True)
    return languages

def read(languages, from_lang, to_lang):
    '''
    Read the dictionaries for a language pair.
    '''
    ds = languages.get(from_lang, {}).get(to_lang)
    for d in ds:
        module = FORMATS[d.format]
        # Packing as a Line is slow. Maybe change this.
        pos, from_word, to_word = module.read(d)
        yield Line(pos, from_lang, from_word, to_lang, to_word)

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
