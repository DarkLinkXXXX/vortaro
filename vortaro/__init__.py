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

from sys import stdout, stderr
from os import environ, makedirs
from pathlib import Path
from collections import OrderedDict
from shutil import get_terminal_size

from sqlalchemy import exists
from sqlalchemy.sql import desc, func
from sqlalchemy.orm import aliased

from .models import (
    SessionMaker, get_or_create,
    History, File, Language, PartOfSpeech, Dictionary, Format,
)
from . import formats

FORMATS = OrderedDict((
    ('dict.cc', formats.dictcc),
    ('cc-cedict', formats.cedict),
    ('espdic', formats.espdic),
))
DATABASE = 'postgresql:///vortaro'
COLUMNS, ROWS = get_terminal_size((80, 20))
DATA = Path(environ.get('HOME', '.')) / '.vortaro'

def Word(x):
    illegal = set('\t\n\r')
    if set(x).issubset(illegal):
        raise ValueError('Word contains forbidden characters.')
    else:
        return x

def download(source: tuple(FORMATS), noindex=False,
        data_dir: Path=DATA, database=DATABASE):
    '''
    Download a dictionary.

    :param source: Dictionary source to download from
    :param pathlib.path data_dir: Vortaro data directory
    :param bool force: Force updating of the index
    :param database: PostgreSQL database URL
    '''
    session = SessionMaker(database)
    subdir = data_dir / source
    makedirs(subdir, exist_ok=True)
    FORMATS[source].download(subdir)
    _index_subdir(session, not noindex, source, subdir)

def index(*sources: tuple(FORMATS), refresh=False,
        data_dir: Path=DATA, database=DATABASE):
    '''
    Index dictionaries.

    :param sources: Dictionary sources to index
    :param pathlib.path data_dir: Vortaro data directory
    :param bool refresh: Replace the existing index.
    :param database: PostgreSQL database URL
    '''
    session = SessionMaker(database)
    for name in sources or FORMATS:
        directory = data_dir / name
        if directory.is_dir() and any(f.is_file() for f in directory.iterdir()):
            _index_subdir(session, refresh, directory.name, directory)

def _index_subdir(session, refresh, format_name, directory):
    for path in directory.iterdir():
        if path.is_file():
            format = get_or_create(session, Format, name=format_name)
            file = get_or_create(session, File, path=str(path), format=format)
            if refresh or file.out_of_date:
                file.update(FORMATS[file.format.name].read, session)
                stderr.write(f'Indexed {path}\n')
                session.commit()

def languages(database=DATABASE):
    '''
    List from-languages that have been indexed.

    :param database: PostgreSQL database URL
    '''
    session = SessionMaker(database)
    q = session.query(Language.code).order_by(Language.code)
    for language, in q.all():
        stdout.write(language + '\n')

def search(text: Word, limit: int=ROWS-2, *, width: int=COLUMNS,
           data_dir: Path=DATA,
           database=DATABASE,
           from_langs: [str]=(), to_langs: [str]=()):
    '''
    Search for a word in the dictionaries.

    :param text: The word/fragment you are searching for
    :param limit: Maximum number of words to return
    :param width: Number of column in a line, or 0 to disable truncation
    :param from_langs: Languages the word is in, defaults to all
    :param to_langs: Languages to look for translations, defaults to all
    :param pathlib.Path data_dir: Vortaro data directory
    :param database: PostgreSQL database URL
    '''
    session = SessionMaker(database)
    ToLanguage = aliased(Language)
    FromLanguage = aliased(Language)
    q_joins = session.query(Dictionary) \
        .join(FromLanguage, Dictionary.from_lang_id == FromLanguage.id) \
        .join(ToLanguage,   Dictionary.to_lang_id   == ToLanguage.id)
    if from_langs:
        q_joins = q_joins.filter(FromLanguage.code.in_(from_langs))
    if to_langs:
        q_joins = q_joins.filter(ToLanguage.code.in_(to_langs))
    q_all = q_joins \
        .filter(func.lower(Dictionary.from_roman).contains(text.lower()))
    q_main = q_all.order_by(Dictionary.from_length).limit(limit)

    # Determine column widths
    meta_tpl = '%%-0%ds\t%%0%ds:%%-0%ds\t%%0%ds:%%s'

    q_lengths = q_all.from_self() \
        .join(PartOfSpeech, Dictionary.part_of_speech_id == PartOfSpeech.id) \
        .with_entities(
            func.max(PartOfSpeech.length),
            func.max(FromLanguage.length),
        #   func.max(Dictionary.from_length)+8,
            func.max(ToLanguage.length),
        )
    row = q_lengths.one()
    if any(row):
        a, b, d = row

        # Don't really look up from length, because it takes too long.
        c_max = int((width - sum(row) + 8) / 2)
        quantile = 1 - min(1, len(text)/limit)
        length = func.length(Dictionary.from_word)
        subq =session.query(length).filter(length > len(text))
        offset = max(0, int(subq.count()*quantile-1))
        c_quantile = subq.order_by(length).offset(offset).limit(1).scalar()
        widths = (a, b, min(c_quantile, c_max), d)

        tpl_line = (meta_tpl % widths).replace('\t', '  ')
        for definition in q_main:
            stdout.write(tpl_line % (
                definition.part_of_speech.text,
                definition.from_lang.code,
                definition.from_highlight(text),
                definition.to_lang.code,
                definition.to_word,
            ) + '\n')
            stdout.flush()

#   session.add(History(
#       text=text,
#       total_results=q_all.count(),
#       displayed_results=limit,
#   ))
#   session.commit()

