from textwrap import wrap
from sys import stdout, stderr, exit
from shutil import get_terminal_size

from requests import get as _get

COLUMNS, ROWS = get_terminal_size((80, 20))

def get(url):
    return _get(url,
                headers={'user-agent': 'https://pypi.python.org/pypi/vortaro'})

def simple_download(url, license, directory):
    for paragraph in license:
        for line in wrap(paragraph, COLUMNS):
            stdout.write(line + '\n')
        stdout.write('\n')
    r = get(url)
    if r.ok:
        return r.content
    else:
        stderr.write('Problem downloading %s\n' % url)
        exit(1)
