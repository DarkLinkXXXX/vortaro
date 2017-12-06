from sys import stdout
from pathlib import Path
from os import environ

def Woerterbuch(from_lang, to_lang):
    filename = '%s-%s.txt' % (from_lang, to_lang)
    p = Path(environ.get('HOME', '.')) / '.dict.cc' / filename
    if p.exists():
        return p.open()
    else:
        raise FileNotFoundError(str(p))

def query_dict(from_lang, to_lang, was_finden):
    with Woerterbuch(from_lang, to_lang).open() as fp:
        for line in fp:
            if line.lower().startswith(was_finden.lower()):
                pass

'\033[4m'

def parse_line(line):
    from_word, to_word, part_of_speech = line.rstrip('\n').split('\t')
	print $erste_spalte, " ", "-"x($laengstes - length($_)), " ", $treffer{$_}, "\n" ;
}
