import re
from sys import stdout
from pathlib import Path
from os import environ

_directory = Path(environ.get('HOME', '.')) / '.dict.cc'
_languages = {}

def open(from_lang, to_lang):
    file = (_directory / ('%s-%s.txt' % (from_lang, to_lang)))
    if to_lang in _languages.get(from_lang, set()):
        return file.open()

def ls(froms=None):
    _index()
    for from_lang in sorted(froms if froms else from_langs()):
        for to_lang in sorted(to_langs(from_lang)):
            yield from_lang, to_lang

def from_langs():
    _index()
    return set(_languages)

def to_langs(from_lang):
    _index()
    return set(_languages.get(from_lang, set()))

def _index():
    if not _languages:
        for file in _directory.iterdir():
            m = re.match(r'^([a-z]+)-([a-z]+)\.txt$', file.name)
            if m:
                f, t = m.groups()
                if f not in _languages:
                    _languages[f] = set()
                _languages[f].add(t)
