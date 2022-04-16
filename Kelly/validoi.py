import datetime

from .veikkaus import listat


def yhdistelma_ok(yhdistelma, systeemi):
    laskuri = 0
    oukkidoukki = False
    for lahto in range(1, systeemi['lahtoja'] + 1):
        lstr = 'L' + str(lahto)
        if yhdistelma[lahto-1] in systeemi[lstr]:
            laskuri += 1
    if laskuri >= systeemi['omia']:
        oukkidoukki = True
    return oukkidoukki


def troikka_yhdistelma_ok(yhdistelma, systeemi):
    laskuri = 0
    oukkidoukki = False
    for y in yhdistelma:
        if y in systeemi['omat']:
            laskuri += 1
        if y in systeemi['tappo']:
            laskuri -= 10
    if laskuri >= systeemi['omia']:
        oukkidoukki = True
    return oukkidoukki


def tarkista_prosentit(pros, filename):
    koodi = filename.split('/')[-1].split('_')[0]
    hepat = hepoja(koodi)
    for lahto in pros.keys():
        pros_lahto = pros[lahto]
        summa = sum(pros_lahto)
        if summa != 100:
            raise Exception(f'Lähtö {lahto}: prosenttien summa {summa}')
        poissa = hepat[lahto]['poissa']
        for pois in poissa:
            if pros_lahto[pois - 1] > 0:
                raise Exception(f'Lähtö {lahto}: Numero {pois} on poissa')


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
                if lahto.runners.has_attr('scratched'):
                    poissa = [pois for pois in lahto.runners['scratched'].split(',')]
                else:
                    poissa = []
                data['poissa'] = poissa
                hepot[lahto['number']] = data
    return hepot


