from sys import stderr, exit
from functools import partial
from .http import simple_download

URL = 'http://www.denisowski.org/Esperanto/ESPDIC/espdic.txt'
LICENSE = (
    'The purpose of the ESPDIC project is to create an electronic Esperanto-English dictionary in the form of a single Unicode (UTF8) text file with the following format :',
	'Esperanto : English',
	'(i.e. Esperanto entry, space, colon, space, English definition - one entry per line). In some cases, a semicolon is used to show different definitions for Esperanto homonyms, e.g. "kajo : conjunction; quay, wharf". This simple formatting is designed to facilitate the integration of ESPDIC into other applications (which is highly encouraged).',
	'In order to encourage its use in the Esperanto community, ESPDIC (Esperanto English Dictionary) by Paul Denisowski is licensed under a Creative Commons Attribution 3.0 Unported License. What this means is that anyone can use, transmit, or modify ESPDIC for any purpose, including commercial purposes, as long as the source is properly attributed.',
)

def download(directory):
    name = URL.split('/')[-1]
    file = (directory / name)
    if file.exists():
        stderr.write('ESPDIC is already downloaded.\n')
        exit(1)
    else:
        body = simple_download(URL, LICENSE, directory)
        with file.open('wb') as fp:
            fp.write(body)
