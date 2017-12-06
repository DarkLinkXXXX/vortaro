from collections import namedtuple

Line = namedtuple('Line', ('from_word', 'to_word', 'part_of_speech'))

class Table(object):
    def __init__(self, search, widths=None, lines=None):
        self.search = search
        self.widths = widths if widths else [0, 0, 0]
        self.lines = lines if lines else []
    def append(self, line):
        for i, text in enumerate(line):
            self._widths[i] = max(columns[i], len(text))
    def __str__(self):
        output = ''
        tpl = '%%-0%ds   %%-0%ds   %%s\n' % self._widths[:2]
        highlighted = line.from_word.replace(self.search, '\033[4m%s\033[4m' % self.search)
        for line in self._lines:
            output += tpl % (highlighted, line.to_word, line.part_of_speech)
        return output
    def __repr__(self):
        return 'Table(search=%s, widths=%s, lines=%s)' % \
            map(repr, (self.search, self.widths, self.lines))
