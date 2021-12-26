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
    config = get_data.get_json(PELIT_FOLDER + 'duo.json')
    pros = {}
    for i in range(2):
        lahto = str(int(args.lahto) + i)
        pros[str(i + 1)] = [p/100 for p in prosentit[lahto]]
    yhdistelmat = list(product(config['L1'], config['L2']))
    omat_tn = []
    panokset = []
    lunastukset = []
    with open(PELIT_FOLDER + 'duo.peli', 'w') as pelifile:
        for yhd in kertoimet:
            yhdistelma = tuple([int(y) for y in yhd['combination'].split('-')])
            if yhdistelma in yhdistelmat:
                kerroin = float(yhd.string.replace(',', '.'))
                if int(kerroin) == 0:
                    kerroin = metadata.jako  # max kerroin jos yhdistelmää ei pelattu
                oma_kerroin = 1 / get_data.yhdistelma_tn(yhdistelma, pros)
                omatn, pelipanos, lunastus = write_to_file(pelifile, yhdistelma, kerroin, oma_kerroin,
                                                           args, config, metadata)
                if lunastus > 0:
                    omat_tn.append(omatn)
                    panokset.append(pelipanos)
                    lunastukset.append(lunastus)
        print(f'Yht;{len(lunastukset)};{sum(panokset):.1f}')
        pelifile.write(f'Yht;{len(lunastukset)};{sum(panokset):.1f}')
    print('<<<<<>>>>>')
    avelunde = sum(lunastukset)/len(lunastukset) if len(lunastukset) > 0 else 0
    footer(omatn, sum(panokset), metadata, min(lunastukset), avelunde, max(lunastukset))


def troikka(args, prosentit, metadata, kertoimet):
    print(f'Troikka: Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    config = get_data.get_json(PELIT_FOLDER + 'troikka.json')
    p1 = [p/100 for p in prosentit[args.lahto]]
    p2 = get_data.p_2(prosentit[args.lahto])
    p3 = get_data.p_3(prosentit[args.lahto])
    omat_tn = []
    panokset = []
    lunastukset = []
    with open(PELIT_FOLDER + 'troikka.peli', 'w') as pelifile:
        for yhd in kertoimet:
            y = [int(y) for y in yhd['combination'].split('-')]
            if get_data.troikka_yhdistelma_ok(y, config):
                kerroin = float(yhd.string.replace(',', '.'))
                if int(kerroin) == 0:
                    kerroin = 2.0 * metadata.jako  # max kerroin jos yhdistelmää ei pelattu
                oma_kerroin = 100000.0
                if (p1[y[0] - 1] * p2[y[1] - 1] * p3[y[2] - 1]) > 0.000001:
                    oma_kerroin = ((1 - p2[y[0] - 1])*(1-p3[y[0] - 1]-p3[y[1] - 1])) / (p1[y[0] - 1]*p2[y[1] - 1]*p3[y[2] - 1])
                omatn, pelipanos, lunastus = write_to_file(pelifile, y, kerroin, oma_kerroin,
                                                           args, config, metadata)
                if lunastus > 0:
                    omat_tn.append(omatn)
                    panokset.append(pelipanos)
                    lunastukset.append(lunastus)
        print(f'Yht;{len(lunastukset)};{sum(panokset):.1f}')
        pelifile.write(f'Yht;{len(lunastukset)};{sum(panokset):.1f}')
    print('<<<<<>>>>>')
    avelunde = sum(lunastukset)/len(lunastukset) if len(lunastukset) > 0 else 0
    footer(sum(omat_tn), sum(panokset), metadata, min(lunastukset), avelunde, max(lunastukset))


def t_peli(args, prosentit, metadata, kertoimet):
    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    config = get_data.get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(config['lahtoja'])
    pros = {}
    for i in range(config['lahtoja']):
        lahto = str(int(args.lahto) + i)
        lahto_t_peli = str(i + 1)
        pros[lahto_t_peli] = [p/100 for p in prosentit[lahto]]
        config['L' + lahto_t_peli] = get_data.split_abcd(pros[lahto_t_peli], config['rajat'])
    rivit = get_data.hajotus_rivit(config)
    omat_tn = []
    panokset = []
    lunastukset = []
    vain_ylin = 1
    if args.pelimuoto in ['t65']:
        vain_ylin = 2
    if args.pelimuoto in ['t64', 't75', 't86']:
        vain_ylin = 2.5

    with open(PELIT_FOLDER + pelimuoto + '.peli', 'w') as pelifile:
        for yhd in kertoimet:
            yhdistelma = tuple([int(y) for y in yhd['combination'].split('-')])
            if yhdistelma in rivit:
                kerroin = vain_ylin * float(yhd.string.replace(',', '.')) / config['panos']
                if int(kerroin) == 0:
                    kerroin = metadata.jako / config['panos'] # max kerroin jos yhdistelmää ei pelattu
                oma_kerroin = 1 / get_data.yhdistelma_tn(yhdistelma, pros)
                omatn, pelipanos, lunastus = write_to_file(pelifile, yhdistelma, kerroin, oma_kerroin,
                                                           args, config, metadata)
                if lunastus > 0:
                    omat_tn.append(omatn)
                    panokset.append(pelipanos)
                    lunastukset.append(lunastus)
        print(f'Yht;{len(lunastukset)};{sum(panokset):.1f}')
        pelifile.write(f'Yht;{len(lunastukset)};{sum(panokset):.1f}')
    print('<<<<<>>>>>')
    avelunde = sum(lunastukset)/len(lunastukset) if len(lunastukset) > 0 else 0
    footer(sum(omat_tn), sum(panokset), metadata, min(lunastukset), avelunde, max(lunastukset))



def t_peli_pros(args, prosentit, metadata, peliprosentit):
    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}: PROSENTIT')
    config = get_data.get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(config['lahtoja'])
    pros = {}
    for i in range(config['lahtoja']):
        lahto = str(int(args.lahto) + i)
        lahto_t_peli = str(i + 1)
        pros[lahto_t_peli] = [p/100 for p in prosentit[lahto]]
        config['L' + lahto_t_peli] = get_data.split_abcd(pros[lahto_t_peli], config['rajat'])
    rivit = get_data.hajotus_rivit(config)

    pelipros = {}
    for key in peliprosentit.keys():
        pelipros[key] = [p/100 for p in peliprosentit[key]]
    omat_tn = []
    panokset = []
    lunastukset = []
    vain_ylin = 1

    with open(PELIT_FOLDER + pelimuoto + '.peli', 'w') as pelifile:
        for yhdistelma in rivit:
            # vain ylin voittoluokka
            kerroin = (metadata.jako / metadata.vaihto) / get_data.yhdistelma_tn(yhdistelma, pelipros)
            oma_kerroin = 1 / get_data.yhdistelma_tn(yhdistelma, pros)
            omatn, pelipanos, lunastus = write_to_file(pelifile, yhdistelma, kerroin, oma_kerroin,
                                                           args, config, metadata)
            if lunastus > 0:
                omat_tn.append(omatn)
                panokset.append(pelipanos)
                lunastukset.append(lunastus)
        print(f'Yht;{len(lunastukset)};{sum(panokset):.1f}')
        pelifile.write(f'Yht;{len(lunastukset)};{sum(panokset):.1f}')
    print('<<<<<>>>>>')
    avelunde = sum(lunastukset)/len(lunastukset) if len(lunastukset) > 0 else 0
    footer(sum(omat_tn), sum(panokset), metadata, min(lunastukset), avelunde, max(lunastukset))


def write_to_file(pelifile, yhdistelma, kerroin, oma_kerroin, args, config, metadata):
    omatn = 0
    pelipanos = 0
    lunastus = 0
    if kerroin > oma_kerroin:
        kelly = get_data.kelly(kerroin, oma_kerroin)
        if config['moninkertaistus']:
            kertaa = int(kelly / config['min_kelly'])
        else:
            kertaa = 1 if kelly > config['min_kelly'] else 0
        lunastus = kertaa * config['panos'] * kerroin
        if lunastus > config['min_lunastus']:
            omatn = (1 / oma_kerroin)
            pelipanos = kertaa * config['panos']
            yhd = '/'.join(yhdistelma)
            txt = (
                f'{metadata.lyhenne};{metadata.pvm};{args.lahto};'
                f'{metadata.peli};{yhd};'
                f'{pelipanos};{pelipanos}'
            )
            print(f'{txt}  =>  {kerroin}')
            pelifile.write(txt + '\n')
    return omatn, pelipanos, lunastus


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