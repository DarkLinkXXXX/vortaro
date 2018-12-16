# vortaro
# Copyright (C) 2017, 2018 Thomas Levine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from sys import stderr
from functools import lru_cache

from .http import simple_download

__all__ = ['download', 'read']

URL = 'http://www.denisowski.org/Esperanto/ESPDIC/espdic.txt'
FILENAME = URL.split('/')[-1]
LICENSE = (
    'The purpose of the ESPDIC project is to create an electronic Esperanto-English dictionary in the form of a single Unicode (UTF8) text file with the following format :',
	'Esperanto : English',
	'(i.e. Esperanto entry, space, colon, space, English definition - one entry per line). In some cases, a semicolon is used to show different definitions for Esperanto homonyms, e.g. "kajo : conjunction; quay, wharf". This simple formatting is designed to facilitate the integration of ESPDIC into other applications (which is highly encouraged).',
	'In order to encourage its use in the Esperanto community, ESPDIC (Esperanto English Dictionary) by Paul Denisowski is licensed under a Creative Commons Attribution 3.0 Unported License. What this means is that anyone can use, transmit, or modify ESPDIC for any purpose, including commercial purposes, as long as the source is properly attributed.',
)

def download(directory):
    file = (directory / FILENAME)
    if file.exists():
        stderr.write('ESPDIC is already downloaded.\n')
    else:
        body = simple_download(URL, LICENSE, directory)
        with file.open('wb') as fp:
            fp.write(body)

def read(path):
    '''
    Read a dictionary file

    :param pathlib.Path path: Dictionary file
    '''
    with path.open() as fp:
        next(fp)
        for rawline in fp:
            l, rs = rawline[:-1].split(' : ')
            for r in rs.split(', '):
                yield {
                    'part_of_speech': _part_of_speech(l[-2:]),
                    'from_lang': 'eo',
                    'from_word': l,
                    'to_lang': 'en',
                    'to_word': r,
                }
                yield {
                    'part_of_speech': _part_of_speech(l[-2:]),
                    'from_lang': 'en',
                    'from_word': r,
                    'to_lang': 'eo',
                    'to_word': l,
                }

POS = (
    ('noun', ('o', 'oj')),
    ('adj',  ('a', 'aj')),
    ('adv',  ('e',)),
    ('verb', ('i', 'is', 'as', 'os', 'u')),
)

@lru_cache(None)
def _part_of_speech(word):
    for pos, suffixes in POS:
        for suffix in suffixes:
            if word.endswith(suffix):
                return pos
    return ''
