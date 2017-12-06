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
from pathlib import Path
from os import environ

_directory = Path(environ.get('HOME', '.')) / '.dict.cc'
_languages = {}

def open(from_lang, to_lang):
    file = (_directory / ('%s-%s.txt' % (from_lang, to_lang)))
    if to_lang in _languages.get(from_lang, set()):
        return file.open()

def ls(froms=None):
    _index()
    for from_lang in sorted(froms if froms else from_langs()):
        for to_lang in sorted(to_langs(from_lang)):
            yield from_lang, to_lang

def from_langs():
    _index()
    return set(_languages)

def to_langs(from_lang):
    _index()
    return set(_languages.get(from_lang, set()))

def _index():
    if not _languages:
        for file in _directory.iterdir():
            m = re.match(r'^([a-z]+)-([a-z]+)\.txt$', file.name)
            if m:
                f, t = m.groups()
                if f not in _languages:
                    _languages[f] = set()
                _languages[f].add(t)
