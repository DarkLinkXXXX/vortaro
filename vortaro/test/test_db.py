import pytest

from .. import db

SEARCH = ((
    ('abcdefghi', {'abcde', 'bcdef', 'cdefg', 'defgh', 'efghi'}),
    ('abcde', {'abcde'}),
    ('abc', {'abc'}),
    ('a', {'a'}),
))

INDEX = ((
    ('abcdefghi', {
        'abcde', 'bcdef', 'cdefg', 'defgh', 'efghi',
        'abcd', 'bcde', 'cdef', 'defg', 'efgh', 'fghi',
        'abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi',
        'ab', 'bc', 'cd', 'de', 'ef', 'fg', 'gh', 'hi',
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
    }),
    ('abcde', {
        'abcde',
        'abcd', 'bcde',
        'abc', 'bcd', 'cde',
        'ab', 'bc', 'cd', 'de',
        'a', 'b', 'c', 'd', 'e',
    }),
    ('abc', {'abc', 'ab', 'bc', 'a', 'b', 'c'}),
))

@pytest.mark.parametrize('phrase, fragments', SEARCH)
def test_search_fragments(phrase, fragments):
    obs = set(db._search_fragments(phrase))
    assert obs == fragments

@pytest.mark.parametrize('phrase, fragments', INDEX)
def test_index_fragments(phrase, fragments):
    obs = set(db._index_fragments(phrase))
    assert obs == fragments
