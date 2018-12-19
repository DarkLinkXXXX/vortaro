import datetime
from urllib.parse import urlsplit
from bz2 import BZ2File

import lxml.html

from .http import get

URL = 'https://dumps.wikimedia.org/backup-index.html'

def hrefs(r, xpath):
    html = lxml.html.fromstring(r.content)
    html.make_links_absolute(r.url)
    return html.xpath(xpath)

def download(directory):
    basename = '%s.html.p' % datetime.date.today()
    r = get(URL, directory / 'index' / basename)
    for index in hrefs(r, '//a[contains(text(), "wiktionary")]/@href')[20:]:
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
            print(gp.read(1000))
    exit()
