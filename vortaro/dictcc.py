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

import re
import webbrowser
from textwrap import wrap
from shutil import get_terminal_size

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

def index(file):
    '''
    :param pathlib.Path directory: Directory containing files
    :returns: (from language, to language) or None
    '''
    with file.open('rb') as fp:
        firstline = fp.readline()[:-1]
    m = re.match(_regex, firstline)
    if m:
        return tuple(x.decode('utf-8').lower() for x in m.groups())

def read(d):
    '''
    Read a dictionary file

    :param dictionaries.Dictionary d: Dictionary
    '''
    with d.path.open() as fp:
        in_header = True
        for rawline in fp:
            if in_header:
                if rawline.startswith('#') or not rawline.strip():
                    continue
                else:
                    in_header = False

            left_word, right_word, pos = rawline[:-1].split('\t')
            if d.reversed:
                to_word, _from_word = left_word, right_word
            else:
                _from_word, to_word = left_word, right_word
            from_word = _from_word.split(' [', 1)[0]
            yield pos, from_word, to_word

