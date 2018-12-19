import re
import datetime
from urllib.parse import urlsplit
from bz2 import BZ2File
from xml.etree import ElementTree

import lxml.html
from pyparsing import (
    Literal, Optional, OneOrMore, NotAny, SkipTo,
    ParseException,
    printables, Word, LineEnd,
)

from .http import get

URL = 'https://dumps.wikimedia.org/backup-index.html'
TRANSLATION_PLUS = re.compile(r'.*{{(.)\+\|.*')
THIS_LANGUAGE = re.compile(r'^==([^=]+)==')

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
            this_language = path.name[:2] # default from file name
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
                    wikilines = _text(buf).split('\n')
                    if t:
                        for wikiline in wikilines:
                            m = re.match(THIS_LANGUAGE, wikiline)
                            if m:
                                this_language = m.group(1)
                                continue

                            if re.match(TRANSLATION_PLUS, wikiline):
                                print(wikiline)
                                try:
                                    print(t.parseString(wikiline))
                                except ParseException:
                                    pass
                    else:
                        for wikiline in wikilines:
                            m = re.match(TRANSLATION_PLUS, wikiline)
                            if m:
                                t = _translations(m.group(1))
                                line = b''
                                gp.seek(0)
                    title = None
                else:
                    line = next(gp)
    exit()

def _text(x):
    return ElementTree.fromstring(x).text

def _translations(t):
    single = (Literal('{{' + t) + Optional('+')).suppress() + OneOrMore(
        Literal('|').suppress() + SkipTo(Literal('|') | Literal('}}').suppress())
    ) + Literal('}}').suppress()
    return (Literal('*') + Word(printables)).suppress() + \
        OneOrMore(single.setParseAction(tuple) + Optional(SkipTo(Literal('{{')).suppress()))
