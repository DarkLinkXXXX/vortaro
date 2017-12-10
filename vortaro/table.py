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

def _sort_results(result):
    return (
        len(result['from_word']),
        result['part_of_speech'],
        result['from_lang'],
        result['from_word'],
        result['to_lang'],
        result['to_word'],
    )

class Table(object):
    def __init__(self, search, results=None):
        self.search = search
        self.results = results if results else []
    def __bool__(self):
        return bool(self.results)
    def add(self, *row):
        self.results.append(row)
    def sort(self):
        self.results.sort(key=_sort_results)
    def render(self, cols, rows):
        '''
        Supporting multibyte characters was a bit annoying. ::

            python3 -m dictcc lookup -from sv är 10
        '''
        tpl_cell = '\033[4m%s\033[0m'
        adj = len(tpl_cell) - 2

        if rows:
            results = self.results[:rows]
        else:
            results = self.results

        widths = [0, 0, 0, 0]
        for line in results:
            row = result['part_of_speech'], \
                result['from_lang'], result['from_word'], \
                result['to_lang'], result['to_word']
            for i, cell in enumerate(row[:-1]):
                widths[i] = max(widths[i], len(cell))
        widths[2] += adj

        tpl_line = '%%-0%ds\t%%-0%ds:%%-0%ds\t%%-0%ds:%%s' % tuple(widths)
        tpl_line = tpl_line.replace('\t', '   ')

        for line in results:
            highlighted = result['from_word'].replace(self.search, tpl_cell % self.search)
            formatted = tpl_line % (
                result['part_of_speech'],
                result['from_lang'], highlighted,
                result['to_lang'], result['to_word'],
            )
            if cols:
                yield formatted[:(cols+adj)] + '\n'
            else:
                yield formatted + '\n'

    def __repr__(self):
        return 'Table(search=%s, widths=%s, results=%s)' % \
            tuple(map(repr, (self.search, self.results)))
