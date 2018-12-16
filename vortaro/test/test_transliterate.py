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

from ..transliterate import ALPHABETS

transliterations = (
    ('bg', 'общопрактикуваща лекарка', 'obštopraktikuvašta lekarka'),
    ('eo', 'ĉu', 'cxu'),
    ('sr', 'чокањчиће', 'čokanjčiće'),
)
@pytest.mark.parametrize('original_to_roman', (True, False))
@pytest.mark.parametrize('language_code, original, roman', transliterations)
def test_highlight(original_to_roman, language_code, original, roman):
    alphabet = ALPHABETS[language_code]
    if original_to_roman:
        assert alphabet.to_roman(original) == roman
    else:
        assert alphabet.from_roman(roman) == original
