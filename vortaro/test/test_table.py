# vortaro
# Copyright (C) 2017, 2018 Thomas Levine
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

import pytest
from .. import table

HIGHLIGHT = (
    ('en', 'elephant', 'PH', ('ele', 'ph', 'ant')),
    ('sr', 'чокањчиће', 'či', ('чокањ', 'чи', 'ће')),
    ('sr', 'чокањчиће', 'njČi', ('чока', 'њчи', 'ће')),
    ('sr', 'чокањчиће', 'jči', ('чокањчиће', '', '')),
)

@pytest.mark.parametrize('lang, big_foreign, small_roman, highlighted', HIGHLIGHT)
def test_highlight(lang, big_foreign, small_roman, highlighted):
    assert table._highlight(lang, big_foreign, small_roman) == highlighted

WIDTHS = (
    ([4, 2, 16, 2], (
         {
             'part_of_speech': 'noun',
             'from_lang': 'en', 'from_word': 'square',
             'to_lang': 'sr', 'to_word': 'трг {м}',
         }, 
         {
             'part_of_speech': 'adj',
             'from_lang': 'en', 'from_word': 'careful',
             'to_lang': 'fr', 'to_word': 'consciencieux [soigneux]',
         },
         {
            'part_of_speech': 'adj',
            'from_lang': 'en', 'from_word': 'apparent',
            'to_lang': 'fr', 'to_word': 'apparent',
        }
    )),
)
@pytest.mark.parametrize('y, x', WIDTHS)
def test_widths(y, x):
    assert table._widths(x) == y
