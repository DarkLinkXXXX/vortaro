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

from logging import getLogger
from pathlib import Path

import horetu

from . import download, index, search, languages, DATA

logger = getLogger(__name__)

def ui():
    config_name = 'config'
    def configure(data_dir: Path=DATA):
        path = data_dir / config_name
        if path.exists():
            raise horetu.Error(f'Configuration file already exists at {path}')
        else:
            with path.open('w') as fp:
                fp.write(horetu.config_default(program))
    program = horetu.Program([
        configure,
        languages,
        index,
        download,
        search,
    ], str(DATA / config_name), name='vortaro')
    horetu.cli(program)
