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
    ('en', 'elephant', 'elephant', 'PH',
        ('ele', 'ph', 'ant')),
    ('en', 'elephant', 'elephant', 'PH',
        '\x1b[1mele\x1b[4mph\x1b[0m\x1b[1mant\x1b[0m'),

    ('bg', 'минерална вода', 'mineralna voda', 'voda',
        ('минерална ', 'вода', '')),
#   ('bg', 'минерална вода', 'mineralna voda', 'voda',
#       '\x1b[0m\x1b[0m\x1b[1mминерална вода\x1b[0m\x1b[0m'),
#   ('bg', 'минерална вода', 'mineralna voda', 'voda',
#       '\033[1mминерална \033[4mвода\033[1m\033[0m'),

    ('bs', 'mineralna voda', 'mineralna voda', 'voda',
        ('mineralna ', 'voda', '')),
    ('bs', 'mineralna voda', 'mineralna voda', 'voda',
        '\x1b[1mmineralna \x1b[4mvoda\x1b[0m\x1b[1m\x1b[0m'),

    ('sr', 'чокањчиће', 'čokanjčiće', 'či',
        ('чокањ', 'чи', 'ће')),
#   ('sr', 'чокањчиће', 'či', 
#       '\x1b[0m\x1b[0m\x1b[1mчокањчиће\x1b[0m\x1b[0m'),
    ('sr', 'чокањчиће', 'čokanjčiće', 'njČi',
        ('чока', 'њчи', 'ће')),
#   ('sr', 'чокањчиће', 'čokanjčiće', 'njČi',
#       '\x1b[0m\x1b[0m\x1b[1mчокањчиће\x1b[0m\x1b[0m'),
    ('sr', 'чокањчиће', 'čokanjčiće', 'jči',
        ('', 'чокањчиће', '')),
#   ('sr', 'чокањчиће', 'čokanjčiće', 'jči',
#       '\x1b[0m\x1b[0m\x1b[1mчокањчиће\x1b[0m\x1b[0m'),
)

@pytest.mark.parametrize('lang, big_foreign, big_roman, small_roman, highlighted', HIGHLIGHT)
def test_highlight(lang, big_foreign, big_roman, small_roman, highlighted):
    obs = highlight(lang, big_foreign, big_roman, small_roman,
        _tuple=isinstance(highlighted, tuple))
    assert obs == highlighted
