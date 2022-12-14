# vortaro
# Copyright (C) 2017, 2018 Thomas Levine
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import CreateColumn
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import (
    sessionmaker,
    column_property, synonym,
    relationship, backref,
)
from sqlalchemy.sql import func
from sqlalchemy import (
    create_engine, CheckConstraint,
    Column, ForeignKey, Index,
    String, Integer, DateTime,
)

from .highlight import highlight
from .transliterate import get_alphabet

Base = declarative_base()

def get_or_create(session, model, tries=1, **kwargs):
    for i in range(tries):
        try:
            return session.query(model).filter_by(**kwargs).one()
        except NoResultFound:
            session.flush()
            created = model(**kwargs)
            try:
                session.add(created)
                session.flush()
                return created
            except IntegrityError:
                session.rollback()
                if i == tries:
                    raise

def SessionMaker(x):
    engine = create_engine(x)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

@compiles(CreateColumn, 'postgresql')
def use_identity(element, compiler, **kw):
    text = compiler.visit_create_column(element, **kw)
    text = text.replace('SERIAL', 'INT GENERATED BY DEFAULT AS IDENTITY')
    return text

def whole_number(name):
    return Column(Integer, CheckConstraint('%s >= 0' % name), nullable=False)

class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, nullable=False, default='now')
    text = Column(String, nullable=False)
    total_results = whole_number('total_results')
    displayed_results = whole_number('displayed_results')

class Format(Base):
    __tablename__ = 'format'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

def _mtime(path):
    return int(Path(path).stat().st_mtime)

class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    path = Column(String, unique=True)
    mtime = Column(Integer, nullable=False, default=int)
    format_id = Column(ForeignKey(Format.id), nullable=False)
    format = relationship(Format)

    @property
    def out_of_date(self):
        return self.mtime < _mtime(self.path)
    def update(file, read, session, chunksize):
        get_pos = table_dict(PartOfSpeech, 'text')
        get_lang = table_dict(Language, 'code')

        # If the database allows it, disable constraints during insert
        try:
            session.execute('SET CONSTRAINTS ALL DEFERRED')
        except OperationalError:
            pass

        file.definitions[:] = []
        session.flush()
        for index, pair in enumerate(read(Path(file.path))):
            alphabet = get_alphabet(pair['from_lang'])
            from_orig = pair['from_word']
            from_roman = alphabet.to_roman(pair['from_word'])
            if from_orig == from_roman:
                from_roman = None
            file.definitions.append(Dictionary(
                file=file, index=index,
                part_of_speech=get_pos(session, pair.get('part_of_speech', '')),
                from_lang=get_lang(session, pair['from_lang']),
                from_original=from_orig,
                from_roman_transliteration=from_roman,
                to_lang=get_lang(session, pair['to_lang']),
                to_word=pair['to_word'],
            ))
            if (index % chunksize) == 0:
                session.commit()
        file.mtime = _mtime(file.path)
        session.add(file)
        session.commit()

class table_dict(object):
    def __init__(self, Model, key):
        self._Model = Model
        self._key = key
        self._cache = {}
    def __call__(self, session, text):
        if text not in self._cache:
            self._cache[text] = get_or_create(session, self._Model, **{self._key: text})
        return self._cache[text]

class PartOfSpeech(Base):
    __tablename__ = 'part_of_speech'
    id = Column(Integer, primary_key=True)
    text = Column(String, unique=True, nullable=False)
    length = column_property(func.length(text))
Index('part_of_speech_length', PartOfSpeech.length)

class Language(Base):
    __tablename__ = 'language'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    length = column_property(func.length(code))
Index('language_length', Language.length)

class Dictionary(Base):
    __tablename__ = 'dictionary'
    file_id = Column(Integer, ForeignKey(File.id), primary_key=True)
    file = relationship(File,
        backref=backref('definitions',
            cascade='save-update, merge, delete, delete-orphan'))
    index = Column(Integer, primary_key=True)

    part_of_speech_id = Column(Integer, ForeignKey(PartOfSpeech.id), nullable=False)
    part_of_speech = relationship(PartOfSpeech)

    from_lang_id = Column(Integer, ForeignKey(Language.id), nullable=False)
    from_lang = relationship(Language, foreign_keys=[from_lang_id])

    # TODO: Allow for queries in both roman and original
    from_original = Column(String, nullable=False)
    from_word = synonym('from_original')
    from_roman_transliteration = Column(String, nullable=True)
    CheckConstraint('from_word != from_roman_transliteration')
    from_roman = column_property(func.coalesce(from_roman_transliteration, from_original))
    from_length = column_property(func.length(from_original))
    def from_highlight(self, search):
        return highlight(
            self.from_lang.code,
            self.from_original,
            self.from_roman_transliteration or self.from_original,
            search,
        )

    to_lang_id = Column(Integer, ForeignKey(Language.id), nullable=False)
    to_lang = relationship(Language, foreign_keys=[to_lang_id])
    to_word = Column(String, nullable=False)
    to_length = column_property(func.length(to_word))

Index('from_length', Dictionary.from_length)
Index('to_length', Dictionary.to_length)
