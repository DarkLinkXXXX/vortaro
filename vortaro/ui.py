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

from logging import getLogger
from pathlib import Path

import horetu
from sqlalchemy.sql import func

from .models import SessionMaker, History, PartOfSpeech, Dictionary
from .highlight import bold, quiet, HIGHLIGHT_COUNT, QUIET_COUNT
from . import (
    DATA,
    download, index, languages,
    _search_query, DATABASE, ROWS, COLUMNS, Word,
)

logger = getLogger(__name__)

def search(text: Word, limit: int=ROWS-2, *,
        width: int=COLUMNS, database=DATABASE,
        from_langs: [str]=(), to_langs: [str]=()):
    '''
    Search for a word in the dictionaries.

    :param text: The word/fragment you are searching for
    :param limit: Maximum number of words to return
    :param from_langs: Languages the word is in, defaults to all
    :param to_langs: Languages to look for translations, defaults to all
    :param database: SQLAlchemy database URL
    '''
    session = SessionMaker(database)
    q_all, FromLanguage, ToLanguage = \
        _search_query(session, from_langs, to_langs, text)
    q_main = q_all \
        .join(PartOfSpeech, Dictionary.part_of_speech_id == PartOfSpeech.id) \
        .order_by(
            Dictionary.from_length,
            PartOfSpeech.text,
            Dictionary.from_word,
            Dictionary.to_word,
       #    FromLanguage.code,
       #    ToLanguage.code,
       )
    if limit > 0:
        q_main = q_main.limit(limit)

    # Determine column widths
    meta_tpl = '%%-0%ds\t%%0%ds:%%-0%ds\t%%0%ds:%%0%ds'
    q_lengths = q_main.from_self() \
        .join(PartOfSpeech, Dictionary.part_of_speech_id == PartOfSpeech.id) \
        .with_entities(
            func.max(PartOfSpeech.length),
            func.max(FromLanguage.length),
            func.max(Dictionary.from_length),
            func.max(ToLanguage.length),
            func.max(Dictionary.to_length),
        )
    row = list(q_lengths.one())
    if any(row):
        if width > 0 and sum(row) > width:
            row[2] -= sum(row) - width
        for i in (0, 1, 3, 4):
            row[i] += QUIET_COUNT
        row[2] += HIGHLIGHT_COUNT
        tpl_line = (meta_tpl % tuple(row)).replace('\t', '  ')
        for definition in q_main:
            line = (tpl_line % (
                quiet(definition.part_of_speech.text),
                quiet(definition.from_lang.code),
                definition.from_highlight(text),
                quiet(definition.to_lang.code),
                bold(definition.to_word),
            ))
            # Remove the white space if POS is empty.
            if row[0] == 0:
                line = line[2:]
            yield line

    session.add(History(
        text=text,
        total_results=q_all.count(),
        displayed_results=limit,
    ))
    session.commit()


def ui():
    config_name = 'config'
    def configure(data_dir: Path=DATA):
        path = data_dir / config_name
        if path.exists():
            raise horetu.Error('Configuration file already exists at %s' % path)
        else:
            with path.open('w') as fp:
                fp.write(horetu.config_default(program))
    program = horetu.Program([
        configure,
        languages,
        index,
        download,
        search,
    ], str(DATA / config_name), name='vortaro')
    horetu.cli(program)
