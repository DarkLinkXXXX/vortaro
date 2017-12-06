from collections import namedtuple

Line = namedtuple('Line', ('from_lang', 'from_word', 'to_lang', 'to_word', 'part_of_speech'))

class Table(object):
    def __init__(self, search, widths=None, lines=None):
        self.search = search
        self.widths = widths if widths else [0, 0, 0, 0, 0]
        self.lines = lines if lines else []
    def append(self, line):
        for i, text in enumerate(line):
            self.widths[i] = max(self.widths[i], len(text))
        self.lines.append(line)
    def __str__(self):
        output = ''
        tpl_line = '%%-0%ds:%%-0%ds\t%%-0%ds:%%-0%ds\t%%s\n' % tuple(self.widths[:-1])
        for line in self.lines:
            tpl_cell = '\033[4m%s\033[0m'
            highlighted = line.from_word.replace(self.search, tpl_cell % self.search)
            output += tpl_line % (
                line.from_lang, highlighted,
                line.to_lang, line.to_word,
                line.part_of_speech,
            )
        return output
    def __repr__(self):
        return 'Table(search=%s, widths=%s, lines=%s)' % \
            tuple(map(repr, (self.search, self.widths, self.lines)))
