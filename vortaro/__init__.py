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

from sys import stdout, stderr
from os import environ, makedirs
from pathlib import Path
from shutil import get_terminal_size

from sqlalchemy import exists
from sqlalchemy.sql import func, or_
from sqlalchemy.orm import aliased

from .models import (
    SessionMaker, get_or_create,
    History, File, Language, PartOfSpeech, Dictionary, Format,
)
from .highlight import bold, quiet, HIGHLIGHT_COUNT, QUIET_COUNT
from .formats import FORMATS

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
    :param bool noindex: Do not update the index
    :param database: PostgreSQL database URL
    '''
    session = SessionMaker(database)
    subdir = data_dir / source
    makedirs(subdir, exist_ok=True)
    FORMATS[source].download(subdir)
    if not noindex:
        _index_subdir(session, False, source, subdir)

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

def languages(database=DATABASE):
    '''
    List from-languages that have been indexed.

    :param database: PostgreSQL database URL
    '''
    session = SessionMaker(database)
    q = session.query(Language.code).order_by(Language.code)
    for language, in q.all():
        stdout.write(language + '\n')

def search(text: Word, limit: int=ROWS-2, *,
           data_dir: Path=DATA,
           database=DATABASE,
           from_langs: [str]=(), to_langs: [str]=()):
    '''
    Search for a word in the dictionaries.

    :param text: The word/fragment you are searching for
    :param limit: Maximum number of words to return
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
    ltext = text.lower()
    q_all = q_joins \
        .filter(or_(
            func.lower(Dictionary.from_roman_transliteration).contains(ltext),
            func.lower(Dictionary.from_original).contains(ltext),
        ))
    q_main = q_all \
        .join(PartOfSpeech, Dictionary.part_of_speech_id == PartOfSpeech.id) \
        .order_by(
            Dictionary.from_length,
            PartOfSpeech.text,
            Dictionary.from_word,
            Dictionary.to_word,
       #    FromLanguage.code,
       #    ToLanguage.code,
       ).limit(limit)

    # Determine column widths
    meta_tpl = '%%-0%ds\t%%0%ds:%%-0%ds\t%%0%ds:%%s'
    q_lengths = q_main.from_self() \
        .join(PartOfSpeech, Dictionary.part_of_speech_id == PartOfSpeech.id) \
        .with_entities(
            func.max(PartOfSpeech.length) + QUIET_COUNT,
            func.max(FromLanguage.length) + QUIET_COUNT,
            func.max(Dictionary.from_length) + HIGHLIGHT_COUNT,
            func.max(ToLanguage.length) + QUIET_COUNT,
        )
    row = q_lengths.one()
    if any(row):
        tpl_line = (meta_tpl % row).replace('\t', '  ')
        for definition in q_main:
            line = (tpl_line % (
                quiet(definition.part_of_speech.text),
                quiet(definition.from_lang.code),
                definition.from_highlight(text),
                quiet(definition.to_lang.code),
                bold(definition.to_word),
            ) + '\n')
            # Remove the white space if POS is empty.
            if row[0] == 0:
                line = line[2:]
            stdout.write(line)
            stdout.flush()

    session.add(History(
        text=text,
        total_results=q_all.count(),
        displayed_results=limit,
    ))
    session.commit()

