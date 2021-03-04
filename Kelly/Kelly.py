# -*- coding: utf-8 -*-
import os
from itertools import product
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
    pros = {}
    for i in range(2):
        lahto = str(int(args.lahto) + i)
        pros[str(i + 1)] = [p/100 for p in prosentit[lahto]]
    yhdistelmat = list(product(duo['L1'], duo['L2']))
    omatn = 0.0
    lkm = 0
    total = 0.0
    minlunde = 100000.0
    maxlunde = 0.0
    avelunde = 0.0

    with open(PELIT_FOLDER + 'duo.peli', 'w') as pelifile:
        for yhd in kertoimet:
            yhdistelma = tuple([int(y) for y in yhd['combination'].split('-')])
            if yhdistelma in yhdistelmat:
                kerroin = float(yhd.string.replace(',', '.'))
                if int(kerroin) == 0:
                    kerroin = metadata.jako  # max kerroin jos yhdistelmää ei pelattu
                oma_kerroin = 1 / get_data.yhdistelma_tn(yhdistelma, pros)

                if kerroin > oma_kerroin:
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
                            f'{metadata.lyhenne};{metadata.pvm};{args.lahto};'
                            f'{metadata.peli};{yhd["combination"].replace("-", "/")};'
                            f'{kertaa*duo["panos"]:.1f};{kertaa*duo["panos"]:.1f}'
                            )
                        print(f'{txt}  =>  {kerroin}')
                        pelifile.write(txt + '\n')
        print(f'Yht;{lkm};{total:.1f}')
        pelifile.write(f'Yht;{lkm};{total:.1f}')
    print('<<<<<>>>>>')
    footer(omatn, total, metadata, minlunde, avelunde, maxlunde)


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
    footer(omatn, total, metadata, minlunde, avelunde, maxlunde)


def t_peli(args, prosentit, metadata, kertoimet):
    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    t_conf = get_data.get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(t_conf['lahtoja'])
    pros = {}
    for i in range(t_conf['lahtoja']):
        lahto = str(int(args.lahto) + i)
        lahto_t_peli = str(i + 1)
        pros[lahto_t_peli] = [p/100 for p in prosentit[lahto]]
        t_conf['L' + lahto_t_peli] = get_data.split_abcd(pros[lahto_t_peli], t_conf['rajat'])
    rivit = get_data.hajotus_rivit(t_conf)

    omatn = 0.0
    lkm = 0
    total = 0.0
    minlunde = 100000.0
    maxlunde = 0.0
    avelunde = 0.0
    vain_ylin = 1
    if args.pelimuoto in ['t65']:
        vain_ylin = 2
    if args.pelimuoto in ['t64', 't75', 't86']:
        vain_ylin = 2.5

    with open(PELIT_FOLDER + pelimuoto + '.peli', 'w') as pelifile:
        for yhd in kertoimet:
            yhdistelma = tuple([int(y) for y in yhd['combination'].split('-')])
            if yhdistelma in rivit:
                kerroin = vain_ylin * float(yhd.string.replace(',', '.')) / t_conf['panos']
                if int(kerroin) == 0:
                    kerroin = metadata.jako / t_conf['panos'] # max kerroin jos yhdistelmää ei pelattu
                oma_kerroin = 1 / get_data.yhdistelma_tn(yhdistelma, pros)

                if kerroin > oma_kerroin:
                    kelly = get_data.kelly(kerroin, oma_kerroin)
                    if t_conf['moninkertaistus']:
                        kertaa = int(kelly / t_conf['min_kelly'])
                    else:
                        kertaa = 1 if kelly > t_conf['min_kelly'] else 0
                    lunde = kertaa * t_conf['panos'] * kerroin
                    if lunde > t_conf['min_lunastus']:
                        lkm += 1
                        omatn += 1 / oma_kerroin
                        total += kertaa * t_conf['panos']
                        avelunde += lunde / oma_kerroin
                        if lunde < minlunde:
                            minlunde = lunde
                        if lunde > maxlunde:
                            maxlunde = lunde
                        txt = (
                            f'{metadata.lyhenne};{metadata.pvm};{args.lahto};'
                            f'{pelimuoto.upper()};{yhd["combination"].replace("-", "/")};'
                            f'{kertaa*t_conf["panos"]:.2f};{kertaa*t_conf["panos"]:.2f}'
                            )
                        print(f'{txt}  =>  {round(lunde)}')
                        pelifile.write(txt + '\n')
        print(f'Yht;{lkm};{total:.2f}')
        pelifile.write(f'Yht;{lkm};{total:.2f}')
    print('<<<<<>>>>>')
    footer(omatn, total, metadata, minlunde, avelunde, maxlunde)


def t_peli_pros(args, prosentit, metadata, peliprosentit):
    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}: PROSENTIT')
    t_conf = get_data.get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(t_conf['lahtoja'])
    pros = {}
    for i in range(t_conf['lahtoja']):
        lahto = str(int(args.lahto) + i)
        lahto_t_peli = str(i + 1)
        pros[lahto_t_peli] = [p/100 for p in prosentit[lahto]]
        t_conf['L' + lahto_t_peli] = get_data.split_abcd(pros[lahto_t_peli], t_conf['rajat'])
    rivit = get_data.hajotus_rivit(t_conf)

    pelipros = {}
    for key in peliprosentit.keys():
        pelipros[key] = [p/100 for p in peliprosentit[key]]

    omatn = 0.0
    lkm = 0
    total = 0.0
    minlunde = 100000.0
    maxlunde = 0.0
    avelunde = 0.0
    vain_ylin = 1

    with open(PELIT_FOLDER + pelimuoto + '.peli', 'w') as pelifile:
        for yhdistelma in rivit:
            # vain ylin voittoluokka
            kerroin = (metadata.jako / metadata.vaihto) / get_data.yhdistelma_tn(yhdistelma, pelipros)
            oma_kerroin = 1 / get_data.yhdistelma_tn(yhdistelma, pros)
            if kerroin > oma_kerroin:
                kelly = get_data.kelly(kerroin, oma_kerroin)
                if t_conf['moninkertaistus']:
                    kertaa = int(kelly / t_conf['min_kelly'])
                else:
                    kertaa = 1 if kelly > t_conf['min_kelly'] else 0
                lunde = kertaa * t_conf['panos'] * kerroin
                if lunde > t_conf['min_lunastus']:
                    lkm += 1
                    omatn += 1 / oma_kerroin
                    total += kertaa * t_conf['panos']
                    avelunde += lunde / oma_kerroin
                    if lunde < minlunde:
                        minlunde = lunde
                    if lunde > maxlunde:
                        maxlunde = lunde
                    yhd = ''
                    for numero in yhdistelma:
                        yhd += str(numero) + '/'
                    txt = (
                        f'{metadata.lyhenne};{metadata.pvm};{args.lahto};'
                        f'{pelimuoto.upper()};{yhd[:-1]};'
                        f'{kertaa*t_conf["panos"]:.2f};{kertaa*t_conf["panos"]:.2f}'
                        )
                    print(f'{txt}  =>  {kerroin}')
                    pelifile.write(txt + '\n')
        print(f'Yht;{lkm};{total:.2f}')
        pelifile.write(f'Yht;{lkm};{total:.2f}')
    print('<<<<<>>>>>')
    footer(omatn, total, metadata, minlunde, avelunde, maxlunde)



def footer(omatn, total, metadata, minlunde, avelunde, maxlunde):
    tomatn = 0.0
    if omatn > 0.0001:
        tomatn = total / omatn
    print(f'Oma todennäköisyys: {100 * omatn:.1f} % // {tomatn:.1f}')
    print(f'Vaihto: {metadata.vaihto} / Jako: {metadata.jako}')
    try:
        print(
            f'Min: {minlunde:.1f} / Average: {avelunde/omatn:.1f} / '
            f'Max: {maxlunde:.1f}'
            )
    except ZeroDivisionError:
        pass
    print('<<<<<>>>>>')