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

import pickle
from os import makedirs
from textwrap import wrap
from functools import partial
from sys import stdout, stderr, exit
from shutil import get_terminal_size

from requests import get as _get

COLUMNS, ROWS = get_terminal_size((80, 20))

def get(url, path=None):
    f = partial(_get, url, headers={'user-agent': 'https://pypi.python.org/pypi/vortaro'})
    if path == None:
        r = f()
    else:
        makedirs(path.parent, exist_ok=True)
        if path.exists():
            with path.open('rb') as fp:
                r = pickle.load(fp)
        else:
            r = f()
            with path.open('wb') as fp:
                pickle.dump(r, fp)
    return r

def simple_download(url, license, directory):
    for paragraph in license:
        for line in wrap(paragraph, COLUMNS):
            stdout.write(line + '\n')
        stdout.write('\n')
    r = get(url)
    if r.ok:
        return r.content
    else:
        stderr.write('Problem downloading %s\n' % url)
        exit(1)
