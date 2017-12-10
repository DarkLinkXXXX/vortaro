import pytest
from .. import table

HIGHLIGHT = (
    ('en', 'elephant', 'PH', ('ele', 'ph', 'ant')),
    ('sr', 'чокањчиће', 'či', ('чокањ', 'чи', 'ће')),
    ('sr', 'чокањчиће', 'njČi', ('чока', 'њчи', 'ће')),
    ('sr', 'чокањчиће', 'jči', ('чокањчиће', '', '')),
)

@pytest.mark.parametrize('lang, big_foreign, small_roman, highlighted', HIGHLIGHT)
def test_highlight(lang, big_foreign, small_roman, highlighted):
    assert table._highlight(lang, big_foreign, small_roman) == highlighted

WIDTHS = (
    ([4, 2, 10, 2], (
         {
             'part_of_speech': 'noun',
             'from_lang': 'en', 'from_word': 'square',
             'to_lang': 'sr', 'to_word': 'трг {м}',
         }, 
         {
             'part_of_speech': 'adj',
             'from_lang': 'en', 'from_word': 'careful',
             'to_lang': 'fr', 'to_word': 'consciencieux [soigneux]',
         },
         {
            'part_of_speech': 'adj',
            'from_lang': 'en', 'from_word': 'apparent',
            'to_lang': 'fr', 'to_word': 'apparent',
        }
    )),
)
@pytest.mark.parametrize('y, x', WIDTHS)
def test_widths(y, x):
    assert table._widths(x) == y
