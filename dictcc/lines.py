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
    def __init__(self, search, widths=None, lines=None):
        self.search = search
        self.widths = widths if widths else [0, 0, 0, 0, 0]
        self.lines = lines if lines else []
    def append(self, line):
        for i, text in enumerate(line):
            self.widths[i] = max(self.widths[i], len(text))
        self.lines.append(line)
    def sort(self):
        self.lines.sort(key=lambda line: (
            len(line.from_word),
            line.part_of_speech,
            line.from_lang,
            line.to_lang,
            line.to_word,
        ))
    def render(self):
        tpl_line = '%%-0%ds\t%%-0%ds:%%-0%ds\t%%-0%ds:%%s\n' % tuple(self.widths[:-1])
        for line in self.lines:
            tpl_cell = '\033[4m%s\033[0m'
            highlighted = line.from_word.replace(self.search, tpl_cell % self.search)
            yield tpl_line % (
                line.part_of_speech,
                line.from_lang, highlighted,
                line.to_lang, line.to_word,
            )
    def __repr__(self):
        return 'Table(search=%s, widths=%s, lines=%s)' % \
            tuple(map(repr, (self.search, self.widths, self.lines)))
