import pytest
from ..wiktionary import _translations

cases = (
    ('ö', '*danska: {{ö+|da|stå}}\n',
        (('da', 'stå'),)
    ),
    ('ö', '*franska: {{ö+|fr|se tenir}}\n',
        (('fr', 'se tenir'),)
    ),
    ('ö', '*franska: {{ö+|fr|se tenir}}, {{ö+|fr|être debout}}\n',
        (('fr', 'se tenir'), ('fr', 'être debout'))),
)
@pytest.mark.parametrize('letter, wikiline, expected', cases)
def test_translations(letter, wikiline, expected):
    observed = _translations(letter).parseString(wikiline)
    assert tuple(observed) == expected
