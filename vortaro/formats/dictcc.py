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

import re
import webbrowser
from sys import stdout, stderr
from textwrap import wrap
from functools import lru_cache
from shutil import get_terminal_size

__all__ = ['download', 'read']

COLUMNS, ROWS = get_terminal_size((80, 20))
PAIR = re.compile(rb'# ([A-Z]+)-([A-Z]+) vocabulary database	compiled by dict\.cc$')

def download(data_dir):
    directions = '''\
The download page will open in a web browser. Download the dictionary
of interest (as zipped text), unzip it, and put the text file inside this
directory: %s/''' % data_dir
    for line in wrap(directions, COLUMNS):
        stdout.write(line + '\n')
    stdout.write('\n')
    stdout.write('Press enter when you are ready.\n')
    input()
    webbrowser.open('https://www1.dict.cc/translation_file_request.php?l=e')

def read(path):
    with path.open('rb') as fp:
        firstline = fp.readline()[:-1]

    m = PAIR.match(firstline)
    if m:
        left_lang, right_lang = (g.decode('utf-8').lower() for g in m.groups())
    else:
        raise StopIteration

    with path.open() as fp:
        in_header = True
        for rawline in fp:
            if in_header:
                if rawline.startswith('#') or not rawline.strip():
                    continue
                else:
                    in_header = False
            cells = rawline[:-1].split('\t')
            try:
                left_word, right_word, pos, *_ = cells
            except Exception as e:
                stderr.write('Could not parse: %s\n' % repr(rawline))
                stderr.write('%s: %s\n' % (e, repr(cells)))
            else:
                yield {
                    'part_of_speech': pos,
                    'from_lang': left_lang,
                    'from_word': _truncate(left_word),
                    'to_lang': right_lang,
                    'to_word': right_word,
                }
                yield {
                    'part_of_speech': pos,
                    'from_lang': right_lang,
                    'from_word': _truncate(right_word),
                    'to_lang': left_lang,
                    'to_word': left_word,
                }

_sep = re.compile(r' [\[{]')
@lru_cache(1)
def _truncate(x):
    return _sep.split(x)[0]
