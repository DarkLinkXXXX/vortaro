from .transliterate import get_alphabet

UNDERLINE = '\033[4m'
NORMAL = '\033[0m'

def highlight(lang, big_foreign, small_roman):
    alphabet = get_alphabet(lang)
    big_roman = alphabet.to_roman(big_foreign)
    if small_roman.lower() in big_roman.lower():
        left = big_roman.lower().index(small_roman.lower())
        right = left + len(small_roman)
        
        y = (
            alphabet.from_roman(big_roman[:left]),
            alphabet.from_roman(big_roman[left:right]),
            alphabet.from_roman(big_roman[right:]),
        )
        if ''.join(y) == big_foreign:
            a, b, c = y
            return a + UNDERLINE + b + NORMAL + c
    return NORMAL + big_foreign + NORMAL

