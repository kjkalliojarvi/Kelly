# -*- coding: utf-8 -*-
import os
from . import get_data

PELIT_FOLDER = os.environ['PELIT_FOLDER']


def voittaja(args, prosentit, metadata, kertoimet):
    p1 = [p/100 for p in prosentit[args.lahto]]
    print(f'Voittaja: Lähtö {args.lahto}, vaihto {metadata.vaihto}')
    for voittaja in kertoimet:
        num = int(voittaja['runner'])
        vkerr = float(voittaja.string.replace(',', '.'))
        omavk = 1000
        if p1[num-1] > 0:
            omavk = 1 / p1[num-1]
        if vkerr > omavk:
            kelly = get_data.kelly(vkerr, omavk)
            if kelly > 0.05:
                print(str(num) + ': ' + '{0:.1f}'.format(vkerr) + ' / ' +
                      '{0:.1f}'.format(omavk) + ' / ' +
                      '{0:.1f}'.format(100*kelly) + ' %')
    print('----- * -----')


def sija(args, prosentit, metadata, kertoimet):
    p1 = [p/100 for p in prosentit[args.lahto]]
    p2 = get_data.p_2(prosentit[args.lahto])
    p3 = get_data.p_3(prosentit[args.lahto])
    print(f'Sija: Lähtö {args.lahto}, vaihto {metadata.vaihto}')
    for sija in kertoimet:
        num = int(sija['runner'])
        yla = float(sija['high-probable'].replace(',', '.'))
        haar = sija['low-probable'] + ' - ' + sija['high-probable']
        sijap = p1[num-1] + p2[num-1] + p3[num-1]
        if sijap > .2:
            if 1/sijap < yla:
                print(str(num) + ': ' + haar + ' / ' + '{0:.2f}'.format(1/sijap))
    print('----- * -----')


def kaksari(args, prosentit, metadata, kertoimet):
    p1 = [p/100 for p in prosentit[args.lahto]]
    p2 = get_data.p_2(prosentit[args.lahto])
    print(f'Kaksari: Lähtö {args.lahto}, vaihto {metadata.vaihto}')
    for kaksari in kertoimet:
        y = [int(y) for y in kaksari['combination'].split('-')]
        kkerr = float(kaksari.string.replace(',', '.'))
        omakk = 100000.0
        if (p1[y[0] - 1] * p2[y[1] - 1]) > .000001:
            omakk = 1 / (p1[y[0]-1]*p2[y[1]-1]/(1-p2[y[0]-1]) + p1[y[1]-1]*p2[y[0]-1]/(1-p2[y[1]-1]))
        if kkerr > omakk:
            kelly = get_data.kelly(kkerr, omakk)
            if kelly > 0.01:
                print(kaksari['combination']+': '+'{0:.1f}'.format(kkerr)+' / '+'{0:.1f}'.format(omakk)+' / '+'{0:.1f}'.format(100*kelly)+' %')
    print('----- * -----')


def duo(args, prosentit, metadata, kertoimet):
    print(f'Duo: Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    duo = get_data.get_json(PELIT_FOLDER + 'duo.json')

    lahto1 = args.lahto
    lahto2 = str(int(lahto1) + 1)
    p1 = [p/100 for p in prosentit[lahto1]]
    p2 = [p/100 for p in prosentit[lahto2]]

    omatn = 0.0
    lkm = 0
    total = 0.0
    minlunde = 100000.0
    maxlunde = 0.0
    avelunde = 0.0

    with open(PELIT_FOLDER + 'duo.peli', 'w') as pelifile:
        for yhd in kertoimet:
            yhdistelma = [int(y) for y in yhd['combination'].split('-')]

            if get_data.yhdistelma_ok(yhdistelma, duo):
                kerroin = float(yhd.string.replace(',', '.'))
                if int(kerroin) == 0:
                    kerroin = metadata.jako  # max kerroin jos yhdistelmää ei pelattu
                oma_kerroin = 10000.0
                if (p1[yhdistelma[0] - 1] * p2[yhdistelma[1] - 1]) > 0.00001:
                    oma_kerroin = 1 / (p1[yhdistelma[0] - 1] * p2[yhdistelma[1] - 1])

                if kerroin > oma_kerroin > 0:
                    kelly = get_data.kelly(kerroin, oma_kerroin)
                    kertaa = int(kelly / duo['min_kelly'])
                    lunde = kertaa * duo['panos'] * kerroin
                    if lunde > duo['min_lunastus']:
                        lkm += 1
                        omatn += 1 / oma_kerroin
                        total += kertaa * duo['panos']
                        avelunde += lunde / oma_kerroin
                        if lunde < minlunde:
                            minlunde = lunde
                        if lunde > maxlunde:
                            maxlunde = lunde
                        txt = metadata.lyhenne + ';' + metadata.pvm + ';'\
                            + lahto1 + ';' + metadata.peli + ';'\
                            + yhd['combination'].replace('-', '/') + ';'
                        ps = '{0:.1f}'.format(kertaa * duo['panos'])
                        print(txt + ps + ';' + ps)
                        pelifile.write(txt + ps + ';' + ps + '\n')
        print('Yht;' + str(lkm) + ';' + '{0:.1f}'.format(total))
        pelifile.write('Yht;' + str(lkm) + ';' + '{0:.1f}'.format(total))
    print('<<<<<>>>>>')
    tomatn = 0.0
    if omatn > 0.0001:
        tomatn = total / omatn
    print('Oma todennäköisyys: ' + '{0:.1f}'.format(100*omatn) + ' % // ' +
          '{0:.1f}'.format(tomatn))
    print(f'Vaihto: {metadata.vaihto} / Jako: {metadata.jako}')
    try:
        print('Min: ' + '{0:.1f}'.format(minlunde) + ' / Average: ' +
              '{0:.1f}'.format(avelunde/omatn) +
              ' / Max: ' + '{0:.1f}'.format(maxlunde))
    except ZeroDivisionError:
        pass
    print('<<<<<>>>>>')


def troikka(args, prosentit, metadata, kertoimet):
    print(f'Troikka: Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    troikka = get_data.get_json(PELIT_FOLDER + 'troikka.json')
    p1 = [p/100 for p in prosentit[args.lahto]]
    p2 = get_data.p_2(prosentit[args.lahto])
    p3 = get_data.p_3(prosentit[args.lahto])

    omatn = 0.0
    lkm = 0
    total = 0.0
    minlunde = 100000.0
    maxlunde = 0.0
    avelunde = 0.0

    with open(PELIT_FOLDER + 'troikka.peli', 'w') as pelifile:
        for yhd in kertoimet:
            y = [int(y) for y in yhd['combination'].split('-')]
            if get_data.troikka_yhdistelma_ok(y, troikka):
                kerroin = float(yhd.string.replace(',', '.'))
                if int(kerroin) == 0:
                    kerroin = 2.0 * metadata.jako  # max kerroin jos yhdistelmää ei pelattu
                oma_kerroin = 100000.0
                if (p1[y[0] - 1] * p2[y[1] - 1] * p3[y[2] - 1]) > 0.000001:
                    oma_kerroin = ((1 - p2[y[0] - 1])*(1-p3[y[0] - 1]-p3[y[1] - 1])) / (p1[y[0] - 1]*p2[y[1] - 1]*p3[y[2] - 1])
                if kerroin > oma_kerroin > 0:
                    kelly = get_data.kelly(kerroin, oma_kerroin)
                    kertaa = int(kelly / troikka['min_kelly'])
                    lunde = kertaa * troikka['panos'] * kerroin
                    if lunde > troikka['min_lunastus']:
                        lkm += 1
                        omatn += 1 / oma_kerroin
                        total += kertaa * troikka['panos']
                        avelunde += lunde / oma_kerroin
                        if lunde < minlunde:
                            minlunde = lunde
                        if lunde > maxlunde:
                            maxlunde = lunde
                        txt = metadata.lyhenne + ';' + metadata.pvm + ';'\
                            + args.lahto + ';' + metadata.peli + ';'\
                            + yhd['combination'].replace('-', '/') + ';'
                        ps = '{0:.1f}'.format(kertaa * troikka['panos'])
                        print(txt + ps + ';' + ps)
                        pelifile.write(txt + ps + ';' + ps + '\n')
        print('Yht;' + str(lkm) + ';' + '{0:.1f}'.format(total))
        pelifile.write('Yht;' + str(lkm) + ';' + '{0:.1f}'.format(total))
    print('<<<<<>>>>>')
    tomatn = 0.0
    if omatn > 0.0001:
        tomatn = total / omatn
    print('Oma todennäköisyys: ' + '{0:.1f}'.format(100*omatn) + ' % // ' + '{0:.1f}'.format(tomatn))
    print(f'Vaihto: {metadata.vaihto} / Jako: {metadata.jako}')
    try:
        print('Min: ' + '{0:.1f}'.format(minlunde) + ' / Average: ' +
              '{0:.1f}'.format(avelunde/omatn) +
              ' / Max: ' + '{0:.1f}'.format(maxlunde))
    except ZeroDivisionError:
        pass
    print('<<<<<>>>>>')


def t_peli(args, prosentit, metadata, kertoimet):
    pass
