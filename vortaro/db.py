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

import pickle
import datetime
from os import makedirs
from collections import Mapping # , MutableSequence

N = 3 # Fragment size

def history(data, search):
    with (data / 'history').open('a') as fp:
        fp.write('%s\t%s\n' % (search, datetime.datetime.now()))

def search(con, x):
    full_alphabet = con.sscan_iter('characters')
    y = x.lower()

    if set(y).issubset(full_alphabet):
        tpl = 'fragment:%s'
        if len(y) >= N:
            phrases = con.sinter(tpl % f for f in set(_smaller_fragments(y)))
        else:
            phrases = con.sunion(tpl % f for f in \
                                 set(_bigger_fragments(full_alphabet, y)))
        for phrase in phrases:
            if y in phrase:
                yield con.hgetall('phrase:%s' % phrase)

def index(con, lines):
    for line in lines:
        for x in line.pop('search_phrases'):
            y = phrase.lower()
            for character in y:
                con.sadd('characters', character)
            for fragment in set(_smaller_fragments(y)):
                con.sadd('fragment:%s' % fragment, y)
            for key, value in line.items():
                con.hset('phrase:%s' % y, key, value)

def _bigger_fragments(full_alphabet, search):
    for left_n in range(N-len(search)):
        right_n = N - left_n
        left_options = permutations(combinations(full_alphabet, left_n))
        right_options = permutations(combinations(full_alphabet, right_n))
        for prefix, suffix in product(left_options, right_options)
            yield prefix + search + suffix

def _smaller_fragments(phrase):
    if len(phrase) >= N:
        yield phrase
    else:
        columns = []
        for i in range(len(phrase)):
            columns.append(phrase[i:i+1-n])
        for letters in zip(*columns):
            yield ''.join(letters)
