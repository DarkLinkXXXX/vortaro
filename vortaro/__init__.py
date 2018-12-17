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

from sys import stderr
from os import environ, makedirs
from pathlib import Path
from collections import namedtuple
from shutil import get_terminal_size

from sqlalchemy.sql import func, or_
from sqlalchemy.orm import aliased

from .models import (
    SessionMaker, get_or_create,
    File, Language, PartOfSpeech, Dictionary, Format,
)
from .formats import FORMATS

DATA = Path(environ.get('HOME', '.')) / '.vortaro'
DATABASE = 'sqlite:///%s/vortaro.sqlite' % DATA
COLUMNS, ROWS = get_terminal_size((80, 20))
CHUNKSIZE = 100000

def Word(x):
    illegal = set('\t\n\r')
    if set(x).issubset(illegal):
        raise ValueError('Word contains forbidden characters.')
    else:
        return x

def download(source: tuple(FORMATS), noindex=False, chunksize: int=CHUNKSIZE,
        data_dir: Path=DATA, database=DATABASE):
    '''
    Download a dictionary.

    :param source: Dictionary source to download from
    :param pathlib.path data_dir: Vortaro data directory
    :param bool noindex: Do not update the index
    :param database: SQLAlchemy database URL
    :param chunksize: Chunk size for commits; lower this if you get a MemoryError
    '''
    session = SessionMaker(database)
    subdir = data_dir / source
    makedirs(subdir, exist_ok=True)
    FORMATS[source].download(subdir)
    if not noindex:
        _index_subdir(session, chunksize, False, source, subdir)

def index(*sources: tuple(FORMATS), refresh=False, chunksize: int=CHUNKSIZE,
        data_dir: Path=DATA, database=DATABASE):
    '''
    Index dictionaries.

    :param sources: Dictionary sources to index
    :param pathlib.path data_dir: Vortaro data directory
    :param bool refresh: Replace the existing index.
    :param database: SQLAlchemy database URL
    :param chunksize: Chunk size for commits; lower this if you get a MemoryError
    '''
    session = SessionMaker(database)
    for name in sources or FORMATS:
        directory = data_dir / name
        if directory.is_dir() and any(f.is_file() for f in directory.iterdir()):
            _index_subdir(session, chunksize, refresh, directory.name, directory)

def _index_subdir(session, chunksize, refresh, format_name, directory):
    for path in directory.iterdir():
        if path.is_file():
            format = get_or_create(session, Format, name=format_name)
            file = get_or_create(session, File, path=str(path), format=format)
            if refresh or file.out_of_date:
                file.update(FORMATS[file.format.name].read, session, chunksize)
                stderr.write('Indexed %s\n' % path)

def languages(database=DATABASE):
    '''
    List from-languages that have been indexed.

    :param database: SQLAlchemy database URL
    '''
    session = SessionMaker(database)
    q = session.query(Language.code).order_by(Language.code)
    for language, in q.all():
        yield language

def _search_query(session, from_langs, to_langs, text):
    ToLanguage = aliased(Language)
    FromLanguage = aliased(Language)
    q = session.query(Dictionary) \
        .join(FromLanguage, Dictionary.from_lang_id == FromLanguage.id) \
        .join(ToLanguage,   Dictionary.to_lang_id   == ToLanguage.id)
    if from_langs:
        q = q.filter(FromLanguage.code.in_(from_langs))
    if to_langs:
        q = q.filter(ToLanguage.code.in_(to_langs))
    ltext = text.lower()
    q = q.filter(or_(
        func.lower(Dictionary.from_roman_transliteration).contains(ltext),
        func.lower(Dictionary.from_original).contains(ltext),
    ))
    return q, FromLanguage, ToLanguage

SearchResult = namedtuple('SearchResult', (
    'part_of_speech','from_lang', 'from_word', 'to_lang', 'to_word',
))

def search(text: Word, *, database=DATABASE,
        from_langs: [str]=(), to_langs: [str]=()):
    '''
    Search for a word in the dictionaries.

    :param text: The word/fragment you are searching for
    :param from_langs: Languages the word is in, defaults to all
    :param to_langs: Languages to look for translations, defaults to all
    :param database: SQLAlchemy database URL
    '''
    session = SessionMaker(database)
    q, *_ = _search_query(session, from_langs, to_langs, text)
    q = q.join(PartOfSpeech, Dictionary.part_of_speech_id == PartOfSpeech.id) \
        .order_by(
            Dictionary.from_length,
            PartOfSpeech.text,
            Dictionary.from_word,
            Dictionary.to_word,
        #   FromLanguage.code,
        #   ToLanguage.code,
        )
    for definition in q:
        yield SearchResult(
            part_of_speech=definition.part_of_speech.text,
            from_lang=definition.from_lang.code,
            from_word=definition.from_original,
            to_lang=definition.to_lang.code,
            to_word=definition.to_word,
        )
