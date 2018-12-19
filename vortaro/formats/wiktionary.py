import re
import datetime
from urllib.parse import urlsplit
from bz2 import BZ2File
from xml.etree import ElementTree

# import lxml.etree
import lxml.html

from .http import get

URL = 'https://dumps.wikimedia.org/backup-index.html'
TRANSLATION = re.compile(r'{{.\+\|')

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
            title = None
            line = b''
            while True:
                if title == None and line.startswith(b'  <title>'):
                    title = _text(line)
                    line = next(gp)
                elif line.startswith(b'      <text'):
                    buf = line
                    while not line.endswith(b'</text>\n'):
                        line = next(gp)
                        buf += line
                    line = next(gp)
                    print(buf.decode('utf-8'))
                    for wikiline in _text(buf).split('\n'):
                        if re.match(TRANSLATION, wikiline):
                            print(wikiline)
                    title = None
                else:
                    line = next(gp)
    exit()

def _text(x):
    # return str(lxml.etree.fromstring(x).text)
    return ElementTree.fromstring(x).text
