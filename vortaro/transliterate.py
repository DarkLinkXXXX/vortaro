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
        ('а', 'a'),
        ('б', 'b'),
        ('в', 'v'),
        ('г', 'g'),
        ('д', 'd'),
        ('е', 'e'),
        ('ж', 'ž'),
        ('з', 'z'),
        ('и', 'i'),
        ('й', 'y'),
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
        ('ф', 'f'),
        ('х', 'h'),
        ('ц', 'c'),
        ('ч', 'č'),
        ('ш', 'š'),
        ('щ', 'št'),
        ('ъ', 'ǎ'),
        ('ь', 'y'),
        ('ю', 'yu'),
        ('я', 'ya'),
    )),
    eo = Alphabet((
        ('c', 'c'),
        ('ĉ', 'cx'),
        ('g', 'g'),
        ('ĝ', 'gx'),
        ('h', 'h'),
        ('ĥ', 'hx'),
        ('j', 'j'),
        ('ĵ', 'jx'),
        ('s', 's'),
        ('ŝ', 'sx'),
        ('u', 'u'),
        ('ŭ', 'ux'),
    )),
    ru = Alphabet((
        ('а', 'a'),
        ('б', 'b'),
        ('в', 'v'),
        ('г', 'g'),
        ('д', 'd'),
        ('е', 'e'),
        ('ё', 'ë'),
        ('ж', 'ž'),
        ('з', 'z'),
        ('и', 'i'),
        ('й', 'y'),
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
        ('ф', 'f'),
        ('х', 'h'),
        ('ц', 'c'),
        ('ч', 'č'),
        ('ш', 'š'),
        ('щ', 'šč'),
        ('ъ', '"'),
        ('ы', 'y'),
        ('ь', '\''),
        ('э', 'è'),
        ('ю', 'ju'),
        ('я', 'ja'),
    )),
    sr = Alphabet((
        ('а', 'a'),
        ('б', 'b'),
        ('в', 'v'),
        ('г', 'g'),
        ('д', 'd'),
        ('е', 'e'),
        ('ж', 'ž'),
        ('з', 'z'),
        ('и', 'i'),
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
        ('ф', 'f'),
        ('х', 'h'),
        ('ц', 'c'),
        ('ч', 'č'),
        ('ш', 'š'),
        ('ђ', 'dj'),
        ('ј', 'j'),
        ('љ', 'lj'),
        ('њ', 'nj'),
        ('ћ', 'ć'),
        ('џ', 'dž'),
    ))
)
