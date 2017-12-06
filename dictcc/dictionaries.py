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
from sys import stdout
from collections import defaultdict, namedtuple
from pathlib import Path
from os import environ

Dictionary = namedtuple('Dictionary', ('path', 'reversed'))
_directory = Path(environ.get('HOME', '.')) / '.dict.cc'
LANGUAGES = defaultdict(dict)
_regex = re.compile(r'# ([A-Z]+)-([A-Z]+) vocabulary database	compiled by dict\.cc$')
for file in _directory.iterdir():
    if file.name.endswith('.txt'):
        with file.open() as fp:
            firstline = fp.readline().strip()
        m = re.match(_regex, firstline)
        f, t = m.groups()
        LANGUAGES[f][t] = Dictionary(file, False)
        LANGUAGES[t][f] = Dictionary(file, True)

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
