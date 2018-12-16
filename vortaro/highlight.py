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

from functools import partial
from logging import getLogger

from .transliterate import get_alphabet

logger = getLogger(__name__)

UNDERLINE = '\033[4m'
DIM = '\033[2m'
BOLD = '\033[1m'
NORMAL = '\033[0m'
HIGHLIGHT_COUNT = len(BOLD + UNDERLINE + NORMAL + BOLD + NORMAL)
QUIET_COUNT = 0

def quiet(x):
    return x

def bold(x):
    return BOLD + x + NORMAL

def highlight(language_code, big_foreign, big_roman, small_roman, _tuple=False):
    '''
    :param bool _tuple: Return a tuple for testing
    '''
    alphabet = get_alphabet(language_code)
    f = partial(_highlight, alphabet, big_foreign, small_roman)
    if small_roman.lower() in big_roman.lower():
        y = f(big_roman)
    elif (big_foreign != big_roman) and (small_roman.lower() in big_foreign.lower()):
        y = f(big_foreign)
    else:
        logger.debug('Could not highlight: small_roman text not found')

    if y == None:
        if _tuple:
            return '', big_foreign, ''
        else:
            return NORMAL + NORMAL + BOLD + big_foreign + NORMAL + NORMAL
    else:
        if _tuple:
            return y
        else:
            a, b, c = y
            return BOLD + a + UNDERLINE + b + NORMAL + BOLD + c + NORMAL

def _highlight(alphabet, big_foreign, small_roman, big_roman):
    left = big_roman.lower().index(small_roman.lower())
    right = left + len(small_roman)
    
    y = (
        alphabet.from_roman(big_roman[:left]),
        alphabet.from_roman(big_roman[left:right]),
        alphabet.from_roman(big_roman[right:]),
    )
    if ''.join(y) == big_foreign:
        return y
