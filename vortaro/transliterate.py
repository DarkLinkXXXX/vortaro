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

from collections import defaultdict
from functools import lru_cache
from logging import getLogger
from io import StringIO

logger = getLogger(__name__)

@lru_cache(None)
def get_alphabet(code):
    return ALPHABETS.get(code, IDENTITY)

class Alphabet(object):
    def __init__(self, alphabet):
        self._alphabet = alphabet
        self.to_roman = Mapper(alphabet)
        self.from_roman = Mapper(tuple((v,k) for (k,v) in alphabet))
    def __repr__(self):
        return 'Alphabet(%s)' % repr(self._alphabet)

class Mapper(object):
    def __init__(self, alphabet):
        mapping = defaultdict(dict)
        for k, v in alphabet:
            if not 1 <= len(k) <= 2:
                raise ValueError('Character is too long: %s' % k)
            left, right = k if len(k) == 2 else (k, '')
            mapping[left][right] = v
        self._mapping = dict(mapping)

    def __call__(self, word):
        def write(raw, letter):
            upper = any(char.upper() == char and char.lower() != char for char in raw)
            output.write(letter.upper() if upper else letter.lower())

        buf = ''
        input = StringIO(word)
        output = StringIO()
        def options(x):
            return self._mapping[x.lower()]
        def single_char(x):
            y = options(x)
            try:
                return y['']
            except KeyError:
                logger.warning(
                    'A multi-character translateration is specified'
                    'without a single-character transliteration,'
                    'and you are trying to use the single-character translateration.'
                )
                return x
        while True:
            char = input.read(1)
            if char == '':
                if buf:
                    write(buf, single_char(buf))
                break
            elif buf:
                if char.lower() in options(buf):
                    write(buf + char, options(buf)[char.lower()])
                    buf = ''
                elif char.lower() in self._mapping:
                    write(buf + char, single_char(buf))
                    buf = char
                else:
                    write(buf, single_char(buf))
                    output.write(char)
                    buf = ''
            else:
                if char.lower() not in self._mapping:
                    output.write(char)
                elif 1 < len(options(char)):
                    buf = char
                else:
                    output.write(single_char(char))
        return output.getvalue()

IDENTITY = Alphabet(())
ALPHABETS = dict(
    bg = Alphabet((
        ('??', 'a'),
        ('??', 'b'),
        ('??', 'v'),
        ('??', 'g'),
        ('??', 'd'),
        ('??', 'e'),
        ('??', '??'),
        ('??', 'z'),
        ('??', 'i'),
        ('??', 'y'),
        ('??', 'k'),
        ('??', 'l'),
        ('??', 'm'),
        ('??', 'n'),
        ('??', 'o'),
        ('??', 'p'),
        ('??', 'r'),
        ('??', 's'),
        ('??', 't'),
        ('??', 'u'),
        ('??', 'f'),
        ('??', 'h'),
        ('??', 'c'),
        ('??', '??'),
        ('??', '??'),
        ('??', '??t'),
        ('??', '??'),
        ('??', 'y'),
        ('??', 'yu'),
        ('??', 'ya'),
    )),
    eo = Alphabet((
        ('c', 'c'),
        ('??', 'cx'),
        ('g', 'g'),
        ('??', 'gx'),
        ('h', 'h'),
        ('??', 'hx'),
        ('j', 'j'),
        ('??', 'jx'),
        ('s', 's'),
        ('??', 'sx'),
        ('u', 'u'),
        ('??', 'ux'),
    )),
    ru = Alphabet((
        ('??', 'a'),
        ('??', 'b'),
        ('??', 'v'),
        ('??', 'g'),
        ('??', 'd'),
        ('??', 'e'),
        ('??', '??'),
        ('??', '??'),
        ('??', 'z'),
        ('??', 'i'),
        ('??', 'y'),
        ('??', 'k'),
        ('??', 'l'),
        ('??', 'm'),
        ('??', 'n'),
        ('??', 'o'),
        ('??', 'p'),
        ('??', 'r'),
        ('??', 's'),
        ('??', 't'),
        ('??', 'u'),
        ('??', 'f'),
        ('??', 'h'),
        ('??', 'c'),
        ('??', '??'),
        ('??', '??'),
        ('??', '????'),
        ('??', '"'),
        ('??', 'y'),
        ('??', '\''),
        ('??', '??'),
        ('??', 'ju'),
        ('??', 'ja'),
    )),
    sr = Alphabet((
        ('??', 'a'),
        ('??', 'b'),
        ('??', 'v'),
        ('??', 'g'),
        ('??', 'd'),
        ('??', 'e'),
        ('??', '??'),
        ('??', 'z'),
        ('??', 'i'),
        ('??', 'k'),
        ('??', 'l'),
        ('??', 'm'),
        ('??', 'n'),
        ('??', 'o'),
        ('??', 'p'),
        ('??', 'r'),
        ('??', 's'),
        ('??', 't'),
        ('??', 'u'),
        ('??', 'f'),
        ('??', 'h'),
        ('??', 'c'),
        ('??', '??'),
        ('??', '??'),
        ('??', 'dj'),
        ('??', 'j'),
        ('??', 'lj'),
        ('??', 'nj'),
        ('??', '??'),
        ('??', 'd??'),
    ))
)
