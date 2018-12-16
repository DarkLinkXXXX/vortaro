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

import pytest
from ..highlight import highlight

HIGHLIGHT = (
    ('en', 'elephant', 'PH', 'ele\x1b[4mph\x1b[0mant'),
    ('sr', 'чокањчиће', 'či', 'чокањ\x1b[4mчи\x1b[0mће'),
    ('sr', 'чокањчиће', 'njČi', 'чока\x1b[4mњчи\x1b[0mће'),
    ('sr', 'чокањчиће', 'jči', '\x1b[0mчокањчиће\x1b[0m'),
)

@pytest.mark.parametrize('lang, big_foreign, small_roman, highlighted', HIGHLIGHT)
def test_highlight(lang, big_foreign, small_roman, highlighted):
    assert highlight(lang, big_foreign, small_roman) == highlighted
