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

from functools import lru_cache
from pathlib import Path
from gzip import decompress
from sys import stderr, exit

from .lines import EagerLine
from .http import simple_download

LICENSE = (
    'Please observe the copyrights CC-CEDICT.',
    '''\
CC-CEDICT is licensed under a Creative Commons Attribution-Share Alike 3.0
License (http://creativecommons.org/licenses/by-sa/3.0/). It more or less means
that you are allowed to use this data for both non-commercial and commercial
purposes provided that you: mention where you got the data from (attribution)
and that in case you improve / add to the data you will share these changes
under the same license (share alike).''',
    'https://www.mdbg.net/chinese/dictionary?page=cc-cedict',
)
URL = 'https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz'
FILENAME = Path(URL).with_suffix('.txt').name

def download(directory):
    file = (directory / FILENAME)
    if file.exists():
        stderr.write('CC-CEDICT is already downloaded.\n')
        exit(1)
    else:
        body = decompress(simple_download(URL, LICENSE, directory))
        with file.open('wb') as fp:
            fp.write(body)

def index(_):
    return 'zh', 'en'

def read(path):
    '''
    Read a dictionary file

    :param pathlib.Path: Dictionary file
    '''
    with path.open() as fp:
        in_header = True
        for rawline in fp:
            if in_header:
                if rawline.startswith('#'):
                    continue
                else:
                    in_header = False

            traditional, simplified, _rest = rawline[:-1].split(' ', 2)
            _pinyin, *englishes, _ = _rest.split('/')
            pinyin = _pinyin[1:-2]

            for english in englishes:
                yield english, CHINESE % (simplified, pinyin)

CHINESE = '%s [%s]'
class CEDICTLine(EagerLine):
    @property
    def to_word(self):
        x = super(CEDICTLine, self).to_word
        if self.reversed:
            m = re.match(r'([.+]) \[[a-z1-5 ]+\]$', x)
            simplified, pinyin = m.groups()
            return CHINESE % (simplified, _render_pinyin(pinyin))
        else:
            return x


TONES = {
    'a': 'āáǎàa',
    'e': 'ēéěèe',
    'i': 'īíǐìi',
    'o': 'ōóǒòo',
    'u': 'ūúǔùu',
} 

def _render_pinyin(xs):
    return ' '.join(map(_render_syllable, xs.split()))
    
@lru_cache(None)
def _render_syllable(x):
    if x[-1] not in set('12345'):
        return x

    syllable = x[:-1]
    tone = int(x[-1]) - 1
    if 'ao' in syllable:
        original = 'ao'
        replacement = TONES['a'][tone] + 'o'
    else:
        for v in 'aeo':
            if v in syllable:
                original = v
                replacement = TONES[v][tone]
                break
        else:
            for vs in ('iu', 'ui'):
                if vs in syllable:
                    original = vs
                    l, r = vs
                    replacement = l + TONES[r][tone]
                    break
            else:
                return x
    return syllable.replace(original, replacement)
