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

from collections import namedtuple

Line = namedtuple('Line', ('part_of_speech', 'from_lang', 'from_word', 'to_lang', 'to_word'))

class Table(object):
    def __init__(self, search, lines=None):
        self.search = search
        self.lines = lines if lines else []
    def append(self, line):
        self.lines.append(line)
    def sort(self):
        self.lines.sort(key=lambda line: (
            len(line.from_word),
            line.part_of_speech,
            line.from_lang,
            line.to_lang,
            line.to_word,
        ))
    def render(self, cols, rows):
        '''
        Supporting multibyte characters was a bit annoying. ::

            python3 -m dictcc lookup -from sv är 10
        '''
        tpl_cell = '\033[4m%s\033[0m'
        adj = len(tpl_cell) - 2

        if rows:
            lines = self.lines[:rows]
        else:
            lines = self.lines

        widths = [0, 0, 0, 0]
        for line in lines:
            for i, cell in enumerate(line[:-1]):
                widths[i] = max(widths[i], len(cell))
        widths[2] += adj

    #   tpl_line = '{:%d}\t{:%d}:{:%d}\t{:%d}:{}\n' % tuple(widths)
        tpl_line = '%%-0%ds\t%%-0%ds:%%-0%ds\t%%-0%ds:%%s' % tuple(widths)
    #   tpl_line = tpl_line.replace('\t', ' | ')
        tpl_line = tpl_line.replace('\t', '   ')

        for line in lines:
            highlighted = line.from_word.replace(self.search, tpl_cell % self.search)
            formatted = tpl_line % (
                line.part_of_speech,
                line.from_lang, highlighted,
                line.to_lang, line.to_word,
            )
            if cols:
                yield formatted[:(cols+adj)] + '\n'
            else:
                yield formatted + '\n'

    def __repr__(self):
        return 'Table(search=%s, widths=%s, lines=%s)' % \
            tuple(map(repr, (self.search, self.lines)))
