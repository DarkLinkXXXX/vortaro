import re
import datetime
from urllib.parse import urlsplit
from bz2 import BZ2File
from xml.etree import ElementTree

import lxml.html

from .http import get

URL = 'https://dumps.wikimedia.org/backup-index.html'
TRANSLATION_PLUS = re.compile(r'.*{{(.)\+\|.*')

def hrefs(r, xpath):
    html = lxml.html.fromstring(r.content)
    html.make_links_absolute(r.url)
    return html.xpath(xpath)

def download(directory):
    basename = '%s.html.p' % datetime.date.today()
    r = get(URL, directory / 'index' / basename)
    for index in hrefs(r, '//a[contains(text(), "wiktionary")]/@href'):
        path = directory / 'subindex' / urlsplit(index).path[1:] / basename
        r = get(index, path)
        for dump in hrefs(r, '//a[contains(@href, "pages-meta-current.xml.bz2")]/@href'):
            bz2 = directory / ('%s.xml.bz2' % urlsplit(index).path.split('/')[1])
            if not bz2.exists():
                print(bz2)
                r = get(dump)
                with bz2.open('wb') as fp:
                    fp.write(r.content)
            break

def read(path):
    '''
    Read a dictionary file

    :param pathlib.Path: Dictionary file
    '''
    with path.open('rb') as fp:
        with BZ2File(fp) as gp:
            t = None
            title = None
            line = b''
            while True:
                if title == None:
                    if line.startswith(b'    <title>'):
                        title = _text(line)
                    line = next(gp)
                elif line == b'      <text xml:space="preserve" />\n':
                    title = None
                    line = next(gp)
                elif line.startswith(b'      <text'):
                    buf = line
                    while not line.endswith(b'</text>\n'):
                        line = next(gp)
                        buf += line
                    line = next(gp)
                    wikitext = _text(buf)
                    if not t:
                        for wikiline in wikitext.split('\n'):
                            m = re.match(TRANSLATION_PLUS, wikiline)
                            if m:
                                t = m.group(1)
                                title = None
                                line = b''
                                gp.seek(0)
                    title = None
                else:
                    line = next(gp)
    exit()

def _text(x):
    return ElementTree.fromstring(x).text

def _translations(t):
    single = Literal('{{' + t) + Optional('+') + OneOrMore(
        Literal('|') + SkipTo(Literal('|') | Literal('}}'))
    ) + Literal('}}')
    return OneOrMore(single + Optional(NotAny(Literal('}}'))))
