from bs4 import BeautifulSoup
from collections import namedtuple
import datetime
from decouple import config
from io import BytesIO
import requests
import sys
from zipfile import ZipFile


BASEURL = 'https://www.veikkaus.fi/api/toto-info/v1/xml/'
PELIT_FOLDER = config('PELIT_FOLDER')
PROSENTIT_FOLDER = config('PROSENTIT_FOLDER')
metadata = namedtuple('metadata', ['vaihto', 'jako', 'lyhenne', 'pvm', 'peli'])
PVM = datetime.datetime.now().strftime("%d%m%Y")


def tanaan(args):
    pvm = datetime.datetime.now().strftime('%d.%m.%Y')
    for ravit in listat():
        if ravit['date'] == pvm:
            a = ravit.find('pool')['file'].split('_')
            print(ravit['name'], ravit['code'], ravit['track-code'], a[0])


def listat():
    cards = requests.get(BASEURL + 'cards.xml')
    soup = BeautifulSoup(cards.content, 'xml')
    return soup.find_all('card')


def hae_kertoimet(koodi, lahto, peli, compressed=False):
    koodi, lahto, peli = validate_params(koodi, lahto, peli)
    pelifile = f'{koodi}_{PVM}_R{lahto}_{peli}.xml'
    url = f'{BASEURL}{pelifile}'
    if compressed:  # T-pelit
        response = requests.get(url + '.zip')
        if response.content:
            with ZipFile(BytesIO(response.content)) as zipped_file:
                with zipped_file.open(pelifile) as unzipped_file:
                    kerroinxml = unzipped_file.read()
        else:
            print(f'Ei kyseistä peliä: {pelifile}')
            sys.exit(1)
    else:  # muut
        response = requests.get(url)
        if response.content:
            kerroinxml = response.content
        else:
            print(f'Ei kyseistä peliä: {pelifile}')
            sys.exit(1)
    soup = BeautifulSoup(kerroinxml, 'xml')
    kerroindata = soup.find('pool')
    data = metadata(
        vaihto=float(kerroindata['net-sales'].replace(',', '.')),
        jako=float(kerroindata['net-pool'].replace(',', '.')),
        lyhenne=soup.card['code'],
        pvm=soup.card['date'][0:5],
        peli=kerroindata['type'])
    kerroin_gen = _kerroin_gen(soup)
    return data, kerroin_gen


def Tprosentit(koodi, lahto, peli):
    koodi, lahto, peli = validate_params(koodi, lahto, peli)
    url = f'{BASEURL}{koodi}_{PVM}_R{lahto}_{peli}_percs.xml'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    kerroindata = soup.find('pool')
    data = metadata(
        vaihto=float(kerroindata['net-sales'].replace(',', '.')),
        jako=float(kerroindata['net-pool-major-only'].replace(',', '.')),
        lyhenne=soup.card['code'],
        pvm=soup.card['date'][0:5],
        peli=kerroindata['type'])
    all_perc = {}
    for leg in soup.find_all('leg-percentages'):
        legno = leg['leg']
        pr = []
        for perc in leg.find_all('percentage'):
            pr.append(float(perc.string.replace(',', '.')))
        all_perc[legno] = pr
    return data, all_perc


def _kerroin_gen(soup):
    for kerroin in soup.find_all('probable'):
        yield kerroin


def validate_params(koodi, lahto, peli):
    if isinstance(koodi, int):
        koodi = str(koodi)
    if isinstance(lahto, int):
        lahto = str(lahto)
    return koodi, lahto, peli.lower()
