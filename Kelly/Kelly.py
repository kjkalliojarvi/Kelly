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
                print(f'{num:2}: {vkerr:3.1f} / {omavk:3.1f} / {100*kelly:3.1f} %')
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
                print(f'{num:2}: {haar} / {1/sijap:2.2f}')
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
                print(f'{kaksari["combination"]:>5}: '
                      f'{kkerr:5.1f} / {omakk:4.1f} / {100*kelly:4.1f} %')
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
                        txt = (
                            f'{metadata.lyhenne};{metadata.pvm};{lahto1};'
                            f'{metadata.peli};{yhd["combination"].replace("-", "/")};'
                            f'{kertaa*duo["panos"]:.1f};{kertaa*duo["panos"]:.1f}'
                            )
                        print(f'{txt}  =>  {kerroin}')
                        pelifile.write(txt + '\n')
        print(f'Yht;{lkm};{total:.1f}')
        pelifile.write(f'Yht;{lkm};{total:.1f}')
    print('<<<<<>>>>>')
    tomatn = 0.0
    if omatn > 0.0001:
        tomatn = total / omatn
    print(f'Oma todennäköisyys: {omatn:.1f} % // {tomatn:.1f}')
    print(f'Vaihto: {metadata.vaihto} / Jako: {metadata.jako}')
    try:
        print(
            f'Min: {minlunde:.1f} / Average: {avelunde/omatn:.1f} / '
            f'Max: {maxlunde:.1f}'
            )
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
                        txt = (
                            f'{metadata.lyhenne};{metadata.pvm};{args.lahto};'
                            f'{metadata.peli};{yhd["combination"].replace("-", "/")};'
                            f'{kertaa*troikka["panos"]};{kertaa*troikka["panos"]}'
                        )
                        print(f'{txt}  =>  {kerroin}')
                        pelifile.write(txt + '\n')
        print(f'Yht;{lkm};{total:.1f}')
        pelifile.write(f'Yht;{lkm};{total:.1f}')
    print('<<<<<>>>>>')
    tomatn = 0.0
    if omatn > 0.0001:
        tomatn = total / omatn
    print(f'Oma todennäköisyys: {100*omatn:.1f} % // {tomatn:.1f}')
    print(f'Vaihto: {metadata.vaihto} / Jako: {metadata.jako}')
    try:
        print(
            f'Min: {minlunde:.1f} / Average: {avelunde/omatn:.1f} / '
            f'Max: {maxlunde:.1f}')
    except ZeroDivisionError:
        pass
    print('<<<<<>>>>>')


def t_peli(args, prosentit, metadata, kertoimet):
    pass
"""

    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    t_peli = get_data.get_json(PELIT_FOLDER + args.pelimuoto + '.json')
    l = int(lahto)
    pros = Prosentit.pros(koodi)
    p1 = pros[l - 1][:]
    p2 = pros[l][:]
    p3 = pros[l + 1][:]
    p4 = pros[l + 2][:]

    paraf = open('t4_para.txt')
                    # 0 = min Kelly, 1 = panos, 2 = min lunastus
    para = [float(x) for x in paraf.readline().split(',')]

    for line in open('t4.txt'):
        systeemi.append([int(x) for x in line.split(',')])

    kerroinxml = Tkertoimet.bs(koodi, lahto, 't4')

    data = kerroinxml.find('pool')
    vaihto = float(data['net-sales'].replace(',','.'))
    jako = float(data['net-pool'].replace(',','.'))
    lyhenne = kerroinxml.card['code']
    pvm = kerroinxml.card['date'][0:5]
    peli = data['type']

    rivit = {}
    omatn = 0.0
    lkm = 0
    total = 0.0
    minlunde = 100000.0
    maxlunde = 0.0
    avelunde = 0.0
                                                # luetaan data dictionaryyn
    for yhd in kerroinxml.find_all('probable'):
        rivit[yhd['combination']] = {'pelattu': float(yhd['amount'].replace(',','.')), 'kerroin': 5 * float(yhd.string.replace(',', '.')), 'omakerr':0.0}

    heppoja = []
    heppoja = Check.Hepoja(koodi)   
    
    for l1 in range(1,heppoja[l-1][1]+1):
        for l2 in range(1,heppoja[l][1]+1):
            for l3 in range(1,heppoja[l+1][1]+1):
                for l4 in range(1,heppoja[l+2][1]+1):
                    yhd = [l1,l2,l3,l4]
                    pyhd = p1[l1-1] * p2[l2-1]* p3[l3-1] * p4[l4-1]
                    y = "-".join([unicode(x) for x in yhd])
                    if yhdistelma.ok(yhd,systeemi) and pyhd > 0.000001:
                        omakerr = 1 / pyhd
                        if y in rivit.keys():
                            if omakerr > rivit[y]['kerroin']:
                                rivit.pop(y)                # poistetaan ylipelatut kelvolliset rivit
                            else:
                                rivit[y]['omakerr'] = omakerr
                        elif omakerr < 5 * jako:            # pelaamattomat rivit
                            rivit[y] = { 'pelattu': 0.0, 'kerroin' : 5 * jako, 'omakerr' : omakerr}
                    elif y in rivit.keys():
                        rivit.pop(y)                        # poistetaan kelpaamattomat rivit
    
    out = open('/home/kari/Python/Pelit/T4.peli', 'w')
    for yhd in rivit:
        kerroin = rivit[yhd]['kerroin']
        omakerr = rivit[yhd]['omakerr']
        kelly = (kerroin - omakerr) / (kerroin - 1) / omakerr
        kert = int(kelly / para[0])
        lunde = kert * para[1] * kerroin
        if lunde > para[2]:
            lkm += 1
            omatn += 1 / omakerr
            total += kert * para[1]
            avelunde += lunde / omakerr
            if lunde < minlunde:
                minlunde = lunde
            if lunde > maxlunde:
                maxlunde = lunde
            txt = lyhenne + ';' + pvm + ';' + lahto + ';' + peli + ';' + yhd.replace('-', '/') + ';'
            ps = '{0:.1f}'.format(kert * para[1])
            print txt + ps + ';' + ps
            out.write(txt + ps + ';' + ps + '\n')

    print 'Yht;' + str(lkm) + ';' + '{0:.1f}'.format(total)
    out.write('Yht;' + str(lkm) + ';' + '{0:.1f}'.format(total))
    print '<<<<<>>>>>'
    tomatn = 0.0
    if omatn > 0.0001:
        tomatn = total / omatn
    print 'Oma todennäköisyys: ' + '{0:.1f}'.format(100*omatn) + ' % // ' + '{0:.1f}'.format(tomatn)
    print 'Vaihto: ' + '{0:.0f}'.format(vaihto) + ' / Jako: '+ '{0:.0f}'.format(jako)
    print 'Min: ' + '{0:.1f}'.format(minlunde) + ' / Average: ' + '{0:.1f}'.format(avelunde / omatn) + ' / Max: ' + '{0:.1f}'.format(maxlunde)
    print '<<<<<>>>>>'
    out.flush()
    out.close()
    analyysi.Analyysi('/home/kari/Python/Pelit/T4.peli')
"""
