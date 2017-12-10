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
