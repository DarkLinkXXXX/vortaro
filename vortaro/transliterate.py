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

from collections import defaultdict
from io import StringIO

class Alphabet(object):
    def __init__(self, alphabet):
        self._to_roman = alphabet
        self._from_roman = tuple((v,k) for (k,v) in alphabet)

    def __repr__(self):
        return 'Alphabet(%s)' % repr(self._to_roman)
    def to_roman(self, word):
        return self._convert(self._to_roman, word)
    def from_roman(self, word):
        return self._convert(self._from_roman, word)

    @staticmethod
    def _convert(alphabet, word):
        mapping = defaultdict(dict)
        for k, v in alphabet:
            if not 1 <= len(k) <= 2:
                raise ValueError('Character is too long: %s' % k)
            left, right = k if len(k) == 2 else (k, '')
            mapping[left][right] = v
        

        def write(raw, letter):
            upper = any(char.upper() == char and char.lower() != char for char in raw)
            output.write(letter.upper() if upper else letter.lower())

        buf = ''
        input = StringIO(word)
        output = StringIO()
        while True:
            char = input.read(1)
            if char == '':
                if buf:
                    write(buf, mapping[buf.lower()][''])
                break
            elif buf:
                if char.lower() in mapping[buf.lower()]:
                    write(buf + char, mapping[buf.lower()][char.lower()])
                    buf = ''
                elif char.lower() in mapping:
                    write(buf + char, mapping[buf.lower()][''])
                    buf = char
                else:
                    write(buf, mapping[buf.lower()][''])
                    output.write(char)
                    buf = ''
            else:
                if char.lower() not in mapping:
                    output.write(char)
                elif 1 < len(mapping[char.lower()]):
                    buf = char
                else:
                    write(char, mapping[char.lower()][''])
        return output.getvalue()

IDENTITY = Alphabet(())
ALPHABETS = dict(
    sr = Alphabet((
        ('а', 'a'),
        ('б', 'b'),
        ('ц', 'c'),
        ('д', 'd'),
        ('е', 'e'),
        ('ф', 'f'),
        ('г', 'g'),
        ('х', 'h'),
        ('и', 'i'),
        ('ј', 'j'),
        ('к', 'k'),
        ('л', 'l'),
        ('м', 'm'),
        ('н', 'n'),
        ('о', 'o'),
        ('п', 'p'),
        ('р', 'r'),
        ('с', 's'),
        ('т', 't'),
        ('у', 'u'),
        ('в', 'v'),
        ('з', 'z'),
        ('ш', 'š'),
        ('ж', 'ž'),
        ('ћ', 'ć'),
        ('ч', 'č'),
        ('ђ', 'dj'),
        ('џ', 'dž'),
        ('њ', 'nj'),
        ('љ', 'lj'),
    ))
)
