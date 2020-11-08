import requests
import json
from bs4 import BeautifulSoup
import datetime
from zipfile import ZipFile
from io import BytesIO
from collections import namedtuple


BASEURL = 'https://www.veikkaus.fi/api/toto-info/v1/xml/'
metadata = namedtuple('metadata', ['vaihto', 'jako', 'lyhenne', 'pvm', 'peli'])


def prosentit(filename):
    with open(filename, 'r') as prosfile:
        lines = prosfile.read()
        pros = json.loads(lines)
    for lahto in pros.keys():
        pros_summa = sum(pros[lahto])
        if pros_summa != 100:
            raise Exception(f'Lähtö {lahto}: prosenttien summa {pros_summa}')
    return pros


def listat():
    cards = requests.get(BASEURL + 'cards.xml')
    soup = BeautifulSoup(cards.content, 'xml')
    return soup.find_all('card')


def kertoimet(koodi, lahto, peli, compressed=False):
    koodi, lahto, peli = _validate_params(koodi, lahto, peli)
    pvm = datetime.datetime.now().strftime("%d%m%Y")
    pelifile = koodi + '_' + pvm + '_R' + lahto + '_' + peli+'.xml'
    url = BASEURL + pelifile
    if compressed:  # T-pelit
        response = requests.get(url + '.zip')
        with ZipFile(BytesIO(response.content)) as zipped_file:
            kerroinxml = zipped_file.open(pelifile).read()
    else:  # muut
        response = requests.get(url)
        kerroinxml = response.content
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


def _validate_params(koodi, lahto, peli):
    if isinstance(koodi, int):
        koodi = str(koodi)
    if isinstance(lahto, int):
        lahto = str(lahto)
    return koodi, lahto, peli.lower()


def _kerroin_gen(soup):
    for kerroin in soup.find_all('probable'):
        yield kerroin


def Tprosentit(koodi, lahto, peli):
    koodi, lahto, peli = _validate_params(koodi, lahto, peli)
    pvm = datetime.datetime.now().strftime("%d%m%Y")
    url = BASEURL + koodi + '_' + pvm + '_R' + lahto + '_' + peli + '_percs.xml'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'xml')
    all_perc = {}
    for leg in soup.find_all('leg-percentages'):
        legno = leg['leg']
        pr = []
        for perc in leg.find_all('percentage'):
            pr.append(float(perc.string.replace(',', '.')))
        all_perc[legno] = pr
    return all_perc


def hepoja(koodi):
    if isinstance(koodi, int):
        koodi = str(koodi)
    kaikki_ravit = listat()
    pvm = datetime.datetime.now().strftime('%d.%m.%Y')
    hepot = {}
    for ravit in kaikki_ravit:
        if ravit['date'] == pvm and ravit['track-code'] == koodi:
            for lahto in ravit.find_all('race'):
                data = {'hevosia': int(lahto.runners.string)}
                poissa = []
                if lahto.runners.has_attr('scratched'):
                    a = lahto.runners['scratched'].split(',')
                    for i in range(len(a)):
                        poissa.append(int(a[i]))
                data['poissa'] = poissa
                hepot[lahto['number']] = data
    return hepot


def kelly(kerroin, oma_kerroin):
    return (kerroin - oma_kerroin) / (kerroin - 1) / oma_kerroin


def p_2(p):
    kaksip = [0.0, 2.0, 4.2, 6.2, 8.0, 8.7, 9.6, 10.1, 11.2, 12.1,
              12.8, 13.7, 14.4, 15.0, 15.6, 16.0, 16.4, 16.7, 17.2, 17.7,
              18.0, 18.4, 18.55, 18.85, 19.0, 19.35, 19.35, 19.5, 19.3, 19.2,
              19.1, 19.0, 19.0, 19.0, 18.95, 18.9, 18.8, 18.7, 18.6, 18.6,
              18.5, 18.4, 18.3, 18.2, 18.1, 18.0, 17.85, 17.75, 17.5, 17.3,
              17.0, 16.9, 16.75, 16.6, 16.2, 15.8, 15.5, 15.3, 15.15, 14.9,
              14.5, 14.0, 13.55, 13.0, 12.6, 12.0, 11.4, 10.8, 10.2, 9.6,
              9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0]
    p2 = [kaksip[i] for i in p] + [0.0 for i in range(16 - len(p))]
    p2p = [pp/sum(p2) for pp in p2]
    return p2p


def p_3(p):
    kolmep = [0.0, 4.0, 6.5, 8.6, 9.5, 10.7, 11.2, 11.6, 12.0, 12.3,
              12.5, 12.8, 13.0, 13.2, 13.3, 13.3, 13.2, 13.1, 13.0, 12.9,
              12.8, 12.7, 12.65, 12.55, 12.5, 12.35, 12.25, 12.2, 12.1, 12.0,
              11.9, 11.8, 11.7, 11.6, 11.55, 11.5, 11.3, 11.1, 11.0, 10.9,
              10.8, 10.6, 10.3, 10.0, 9.8, 9.6, 9.45, 9.25, 9.0, 8.8,
              8.6, 8.4, 8.25, 8.1, 8.0, 7.9, 7.8, 7.7, 7.55, 7.4,
              7.2, 7.0, 6.95, 6.8, 6.7, 6.6, 6.5, 6.4, 6.3, 6.2,
              6.1, 5.9, 5.7, 5.5, 5.3, 5.1, 4.9, 4.7, 4.5, 4.3, 4.1]
    p3 = [kolmep[i] for i in p] + [0.0 for i in range(16 - len(p))]
    p3p = [pp/sum(p3) for pp in p3]
    return p3p


def yhdistelma_ok(yhdistelma, systeemi):
    laskuri = 0
    oukkidoukki = False
    for lahto in range(1, len(yhdistelma)+1):
        lstr = 'L' + str(lahto)
        if yhdistelma[lahto-1] in systeemi[lstr]:
            laskuri += 1
    if laskuri >= systeemi['oikein']:
        oukkidoukki = True
    return oukkidoukki


def troikka_yhdistelma_ok(yhdistelma, systeemi):
    laskuri = 0
    oukkidoukki = False
    for y in yhdistelma:
        if y in systeemi['ideat']:
            laskuri += 1
        if y in systeemi['tapot']:
            laskuri -= 10
    if laskuri >= systeemi['ideoita']:
        oukkidoukki = True
    return oukkidoukki


def tarkista_prosentit(filename):
    koodi = filename.split('/')[-1].split('_')[0]
    pros = prosentit(filename)
    hepat = hepoja(koodi)
    print('        <<< Ravit ' + koodi + ' >>>')
    for lahto in pros.keys():
        pros_lahto = pros[lahto]
        summa = sum(pros_lahto)
        if summa != 100:
            print('        Lähtö ' + lahto +
                  ': Prosenttien summa ei ole 100 (' + str(summa) + ')')
        poissa = hepat[lahto]['poissa']
        for pois in poissa:
            if pros_lahto[pois - 1] > 0:
                print('        Lähtö ' + lahto + ': Numero ' + str(pois) +
                      ' on poissa')
    print('        ================')


def analyysi(pelifile):
    pelif = open(pelifile)
    rivi = []
    rivi0 = pelif.readline().split(';')
    rivi = [int(x) for x in rivi0[4].split('/')]
    panos = float(rivi0[5])
    pelit = {'DUO': 2, 'TRO': 3, 'T4': 4, 'T5': 5, 'T6': 6, 'T65': 6,
             'T7': 7, 'T75': 7}
    lahtoja = pelit[rivi0[3]]
    laskuri = [[0 for i in range(16)] for j in range(lahtoja)]
    kokpanos = [[0.0 for i in range(16)] for j in range(lahtoja)]
    riveja = 0
    total = 0.0
    while True:
        for ll in range(lahtoja):
            # print ll
            laskuri[ll][rivi[ll]] += 1
            kokpanos[ll][rivi[ll]] += panos
        rivi0 = pelif.readline().split(';')
        if rivi0[0] == 'Yht':
            riveja = rivi0[1]
            total = rivi0[2]
            break
        else:
            rivi = [int(x) for x in rivi0[4].split('/')]
            panos = float(rivi0[5])
    print('Rastit' + str(riveja))
    for i in range(16):
        print('{0:3d} |'.format(i+1), end="")
    print('')
    for i in range(16):
        print('=====', end="")
    print('')
    for ll in range(lahtoja):
        for h in range(16):
            print('{0:3d} |'.format(laskuri[ll][h]), end="")
        print('')
    print('Rastit ')
    a = 0
    for i in range(16):
        print('{0:3d} |'.format(i+1), end="")
    print('')
    for i in range(16):
        print('==== ', end="")
    print('')
    for ll in range(lahtoja):
        a = 0
        for h in range(16):
            print('{0:3d} |'.format(laskuri[ll][h]), end="")
            a += laskuri[ll][h]
        print(a)
    print('%-osuudet')
    for i in range(16):
        print('{0:3d} |'.format(i+1), end="")
    print('')
    for i in range(16):
        print('=====', end="")
    print('')
    for ll in range(lahtoja):
        for h in range(16):
            print('{0:3.0f} |'.format(100*float(laskuri[ll][h])/float(riveja)), end="")
        print('')
    print('%-osuudet rahasta')
    for i in range(16):
        print('{0:3d} |'.format(i+1), end="")
    print('')
    for i in range(16):
        print('=====', end="")
    print('')
    for ll in range(lahtoja):
        for h in range(16):
            print('{0:3.0f} |'.format(100*float(kokpanos[ll][h])/float(total)), end="")
        print('')
