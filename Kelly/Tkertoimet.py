__author__ = 'kari'

import urllib
from bs4 import BeautifulSoup
import datetime
import zipfile
import os

def bs(koodi,lahto,peli):
    pvm = datetime.datetime.now().strftime('%d%m%Y')
    pelifile = koodi + '_' + pvm + '_R' + lahto + '_' + peli+'.xml'
    pelizip = pelifile + '.zip'
    urlzip = 'https://www.fintoto.fi/xml/' + pelizip
    urllib.urlretrieve(urlzip, pelizip) 
    with zipfile.ZipFile(pelizip) as zf:
        zf.extract(pelifile,'/home/kari/Python/Koodi')
    kerroinxml = open(pelifile)
    soup = BeautifulSoup(kerroinxml, 'xml')
    os.remove(pelizip)
    kerroinxml.close()
    os.remove(pelifile)
    return soup
