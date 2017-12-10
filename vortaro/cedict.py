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

from pathlib import Path
from gzip import decompress

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

def download(directory):
    name = Path(URL).with_suffix('.txt').name
    body = decompress(simple_download(URL, LICENSE, directory))
    with (directory / name).open('wb') as fp:
        fp.write(body)
