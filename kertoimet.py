__author__ = 'kari'

import urllib
from bs4 import BeautifulSoup
import datetime

def bs(koodi,lahto,peli):
    pvm = datetime.datetime.now().strftime('%d%m%Y')
    pelifile = koodi + '_' + pvm + '_R' + lahto + '_' + peli+'.xml'
    urlfile = 'https://www.fintoto.fi/xml/' + pelifile
    kerroinxml = urllib.urlopen(urlfile).read()
    soup = BeautifulSoup(kerroinxml, 'xml')
    return soup
