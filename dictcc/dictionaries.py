# Tom's dict.cc dictionary reader
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
from collections import defaultdict, namedtuple
from pathlib import Path
from os import environ

INDEX = 'index.p'
Dictionary = namedtuple('Dictionary', ('path', 'reversed'))
DIRECTORY = Path(environ.get('HOME', '.')) / '.dict.cc'

def build_index(directory):
    languages = defaultdict(dict)
    _regex = re.compile(rb'# ([A-Z]+)-([A-Z]+) vocabulary database	compiled by dict\.cc$')
    for file in directory.iterdir():
        if file.name != INDEX:
            with file.open('rb') as fp:
                firstline = fp.readline().strip()
            m = re.match(_regex, firstline)
            if m:
                f, t = (x.decode('utf-8').lower() for x in m.groups())
                languages[f][t] = Dictionary(file, False)
                languages[t][f] = Dictionary(file, True)
    return languages

def open(from_lang, to_lang):
    return LANGUAGES.get(from_lang, {}).get(to_lang)

def ls(froms=None):
    for from_lang in sorted(froms if froms else from_langs()):
        for to_lang in sorted(to_langs(from_lang)):
            yield from_lang, to_lang

def from_langs():
    return set(LANGUAGES)

def to_langs(from_lang):
    return set(LANGUAGES.get(from_lang, set()))

def _mtime(path):
    return path.stat().st_mtime

# Load language mappings.
_mtimes = tuple(_mtime(f) for f in DIRECTORY.iterdir() if f.name != INDEX)
if _mtimes:
    if (not (DIRECTORY/INDEX).exists()) or \
            (max(_mtimes) > _mtime(DIRECTORY/INDEX)):
        LANGUAGES = build_index(DIRECTORY)
        with (DIRECTORY / INDEX).open('wb') as fp:
            pickle.dump(LANGUAGES, fp)
    else:
        with (DIRECTORY / INDEX).open('rb') as fp:
            LANGUAGES = pickle.load(fp)
else:
    LANGUAGES = {}
