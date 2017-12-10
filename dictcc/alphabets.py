from collections import defaultdict
from io import StringIO

class Alphabet(object):
    def __init__(self, alphabet):
        self.alphabet = alphabet
    def to_roman(self, word):
        return self._convert(False, word)
    def from_roman(self, x):
        return self._convert(True, word)
        
    def _convert(self, swap, word):
        if not self.alphabet:
            return word

        if swap:
            alphabet = tuple((b,a) for (a,b) in self.alphabet)
        else:
            alphabet = self.alphabet

        mapping = defaultdict(dict)
        for k, v in alphabet:
            if not 1 <= len(k) <= 2:
                raise ValueError('Character is too long: %s' % k)
            left, right = k if len(k) == 2 else (k, '')
            mapping[left][right] = v
        

        def write(raw, letter):
            upper = any(char.upper() == char and char.lower() != char for char in raw)
            output.write(letter.upper() if upper else letter.lower())

        buf = ''
        input = StringIO(word)
        output = StringIO()
        while True:
            char = input.read(1)
            if char == '':
                if buf:
                    write(buf, mapping[buf.lower()][''])
                break
            elif buf:
                if char.lower() in mapping[buf.lower()]:
                    write(buf + char, mapping[buf.lower()][char.lower()])
                    buf = ''
                elif char.lower() in mapping:
                    write(buf + char, mapping[buf.lower()][''])
                    buf = char
                else:
                    write(buf, mapping[buf.lower()][''])
                    output.write(char)
                    buf = ''
            else:
                if char.lower() not in mapping:
                    output.write(char)
                elif 1 < len(mapping[char.lower()]):
                    buf = char
                else:
                    write(char, mapping[char.lower()][''])
        return output.getvalue()

identity = Alphabet(())
sr = Alphabet((
    ('а', 'a'),
    ('б', 'b'),
    ('ц', 'c'),
    ('д', 'd'),
    ('е', 'e'),
    ('ф', 'f'),
    ('г', 'g'),
    ('х', 'h'),
    ('и', 'i'),
    ('ј', 'j'),
    ('к', 'k'),
    ('л', 'l'),
    ('м', 'm'),
    ('н', 'n'),
    ('о', 'o'),
    ('п', 'p'),
    ('р', 'r'),
    ('с', 's'),
    ('т', 't'),
    ('у', 'u'),
    ('в', 'v'),
    ('з', 'z'),
    ('ш', 'š'),
    ('ж', 'ž'),
    ('ћ', 'ć'),
    ('ч', 'č'),
    ('ђ', 'dj'),
    ('џ', 'dž'),
    ('њ', 'nj'),
    ('љ', 'lj'),
))
