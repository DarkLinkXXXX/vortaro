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

from .transliterate import get_alphabet

UNDERLINE = '\033[4m'
NORMAL = '\033[0m'

def highlight(lang, big_foreign, small_roman):
    alphabet = get_alphabet(lang)
    big_roman = alphabet.to_roman(big_foreign)
    if small_roman.lower() in big_roman.lower():
        left = big_roman.lower().index(small_roman.lower())
        right = left + len(small_roman)
        
        y = (
            alphabet.from_roman(big_roman[:left]),
            alphabet.from_roman(big_roman[left:right]),
            alphabet.from_roman(big_roman[right:]),
        )
        if ''.join(y) == big_foreign:
            a, b, c = y
            return a + UNDERLINE + b + NORMAL + c
    return NORMAL + big_foreign + NORMAL

