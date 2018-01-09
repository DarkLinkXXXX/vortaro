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

from .transliterate import ALPHABETS, IDENTITY

UNDERLINE = '\033[4m'
NORMAL = '\033[0m'

def _sort_results(result):
    return (
        len(result['from_word']),
        result['part_of_speech'],
        result['from_word'],
        result['to_word'],
        result['from_lang'],
        result['to_lang'],
    )

class Table(object):
    def __init__(self, search, results=None):
        self.search = search
        self.results = results if results else []
    def __bool__(self):
        return bool(self.results)
    def add(self, row):
        if 'part_of_speech' not in row:
            row['part_of_speech'] = ''
        self.results.append(row)
    def __len__(self):
        return len(self.results)
    def sort(self):
        self.results.sort(key=_sort_results)
    def render(self, cols, rows):
        '''
        Supporting multibyte characters was a bit annoying. ::

            python3 -m dictcc lookup -from sv är 10
        '''
        if rows:
            results = self.results[:rows]
        else:
            results = self.results

        widths = _widths(results)

        tpl_line = '%%-0%ds\t%%-0%ds:%%-0%ds\t%%-0%ds:%%s' % tuple(widths)
        tpl_line = tpl_line.replace('\t', '   ')

        for result in results:
            formatted = tpl_line % (
                result['part_of_speech'],
                result['from_lang'],
                highlight(result['from_lang'], result['from_word'], self.search),
                result['to_lang'],
                result['to_word'],
            )
            yield formatted + '\n'

    def __repr__(self):
        return 'Table(search=%s, widths=%s, results=%s)' % \
            tuple(map(repr, (self.search, self.results)))

def highlight(lang, big_foreign, small_roman):
    alphabet = ALPHABETS.get(lang, IDENTITY)
    big_roman = alphabet.to_roman(big_foreign)

    if small_roman.lower() in big_roman.lower():
        left = big_roman.lower().index(small_roman.lower())
        right = left + len(small_roman)
        
        y = (
            alphabet.from_roman(big_roman[:left]),
            alphabet.from_roman(big_roman[left:right]),
            alphabet.from_roman(big_roman[right:]),
        )
        if ''.join(y) == big_foreign:
            a, b, c = y
            return a + UNDERLINE + b + NORMAL + c
    return big_foreign + NORMAL + NORMAL

def _widths(results):
    widths = [0, 0, 0, 0]
    for result in results:
        row = result['part_of_speech'], \
            result['from_lang'], result['from_word'], \
            result['to_lang'], result['to_word']
        for i, cell in enumerate(row[:-1]):
            widths[i] = max(widths[i], len(cell))
    return widths

def Stream(search, cols, result):
    widths = (16, 8, 28, 8)
    tpl_line = '%%-0%ds\t%%0%ds:%%-0%ds\t%%0%ds:%%s' % widths
    tpl_line = tpl_line.replace('\t', '   ')

    formatted = tpl_line % (
        result['part_of_speech'],
        result['from_lang'],
        highlight(result['from_lang'], result['from_word'], search),
        result['to_lang'],
        result['to_word'],
    )
    return formatted + '\n'
