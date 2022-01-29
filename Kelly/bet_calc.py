from collections import namedtuple
import datetime
from decouple import config
from itertools import product
from math import prod

from . import get_data
from . import hajota
from .validoi import troikka_yhdistelma_ok
from .veikkaus import hae_kertoimet, Tprosentit
from .util import write_to_file

PELIT_FOLDER = config('PELIT_FOLDER')
PROSENTIT_FOLDER = config('PROSENTIT_FOLDER')
PVM = datetime.datetime.now().strftime("%d%m%Y")
Bet = namedtuple('Bet', ['yhdistelma', 'kerroin', 'oma_kerroin', 'pelipanos'])



def peli(args):
    filename = f'{PROSENTIT_FOLDER}{args.ratakoodi}_{PVM}.json'
    prosentit = get_data.prosentit(filename)
    if args.pelimuoto in ['voi', 'sij', 'kak', 'duo', 'tro']:
        kutsu = {'voi': voittaja, 'sij': sija, 'kak': kaksari,
                 'tro': troikka, 'duo': duo}
        metadata, kertoimet = hae_kertoimet(args.ratakoodi,
                                                 args.lahto,
                                                 args.pelimuoto)
        kutsu[args.pelimuoto](args, prosentit, metadata, kertoimet)
    if args.pelimuoto in ['t4', 't5', 't64', 't65', 't75', 't86']:
        if args.prosentit:
            metadata, peliprosentit = Tprosentit(args.ratakoodi,
                                                          args.lahto,
                                                          args.pelimuoto)
            t_peli_pros(args, prosentit, metadata, peliprosentit)
        else:
            metadata, kertoimet = hae_kertoimet(args.ratakoodi,
                                                     args.lahto,
                                                     args.pelimuoto,
                                                     compressed=True)
            t_peli(args, prosentit, metadata, kertoimet)


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
            okelly = kelly(vkerr, omavk)
            if okelly > 0.05:
                print(f'{num:2}: {vkerr:3.1f} / {omavk:3.1f} / {100*okelly:3.1f} %')
    print('----- * -----')


def sija(args, prosentit, metadata, kertoimet):
    p1 = [p/100 for p in prosentit[args.lahto]]
    p2 = p_2(prosentit[args.lahto])
    p3 = p_3(prosentit[args.lahto])
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
    p2 = p_2(prosentit[args.lahto])
    print(f'Kaksari: Lähtö {args.lahto}, vaihto {metadata.vaihto}')
    for kaksari in kertoimet:
        y = [int(y) for y in kaksari['combination'].split('-')]
        kkerr = float(kaksari.string.replace(',', '.'))
        omakk = 100000.0
        if (p1[y[0] - 1] * p2[y[1] - 1]) > .000001:
            omakk = 1 / (p1[y[0]-1]*p2[y[1]-1]/(1-p2[y[0]-1]) + p1[y[1]-1]*p2[y[0]-1]/(1-p2[y[1]-1]))
        if kkerr > omakk:
            okelly = kelly(kkerr, omakk)
            if okelly > 0.01:
                print(f'{kaksari["combination"]:>5}: '
                      f'{kkerr:5.1f} / {omakk:4.1f} / {100*okelly:4.1f} %')
    print('----- * -----')


def duo(args, prosentit, metadata, kertoimet):
    print(f'Duo: Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    conf = get_data.get_json(PELIT_FOLDER + 'duo.json')
    pros = {}
    for i in range(2):
        lahto = str(int(args.lahto) + i)
        pros[str(i + 1)] = [p/100 for p in prosentit[lahto]]
    yhdistelmat = list(product(conf['L1'], conf['L2']))
    bets = []
    for yhd in kertoimet:
        y = tuple([int(y) for y in yhd['combination'].split('-')])
        if y in yhdistelmat:
            kerroin = float(yhd.string.replace(',', '.'))
            if int(kerroin) == 0:
                kerroin = metadata.jako  # max kerroin jos yhdistelmää ei pelattu
            oma_kerroin = 1 / yhdistelma_tn(y, pros)
            yhdistelma = yhd['combination'].replace('-', '/')
            bet = bet_size(kerroin, oma_kerroin, yhdistelma, conf)
            if bet:
                bets.append(bet)
    write_to_file(bets, 'duo', args, metadata)


def troikka(args, prosentit, metadata, kertoimet):
    print(f'Troikka: Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    conf = get_data.get_json(PELIT_FOLDER + 'troikka.json')
    p1 = [p/100 for p in prosentit[args.lahto]]
    p2 = p_2(prosentit[args.lahto])
    p3 = p_3(prosentit[args.lahto])
    bets = []
    for yhd in kertoimet:
        y = [int(y) for y in yhd['combination'].split('-')]
        if troikka_yhdistelma_ok(y, conf):
            kerroin = float(yhd.string.replace(',', '.'))
            if int(kerroin) == 0:
                kerroin = 2.0 * metadata.jako  # max kerroin jos yhdistelmää ei pelattu
            oma_kerroin = 100000.0
            if (p1[y[0] - 1] * p2[y[1] - 1] * p3[y[2] - 1]) > 0.000001:
                oma_kerroin = ((1 - p2[y[0] - 1])*(1-p3[y[0] - 1]-p3[y[1] - 1])) / (p1[y[0] - 1]*p2[y[1] - 1]*p3[y[2] - 1])
            yhdistelma = yhd['combination'].replace('-', '/')
            bet = bet_size(kerroin, oma_kerroin, yhdistelma, conf)
            if bet:
                bets.append(bet)
    write_to_file(bets, 'tro', args, metadata)


def t_peli(args, prosentit, metadata, kertoimet):
    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    conf = get_data.get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(conf['lahtoja'])
    pros = {}
    for i in range(conf['lahtoja']):
        lahto = str(int(args.lahto) + i)
        lahto_t_peli = str(i + 1)
        pros[lahto_t_peli] = [p/100 for p in prosentit[lahto]]
        conf['L' + lahto_t_peli] = hajota.split_abcd(pros[lahto_t_peli], conf['rajat'])
    yhdistelmat = hajota.hajotus_rivit(conf)
    vain_ylin = 1
    if args.pelimuoto in ['t65']:
        vain_ylin = 2
    if args.pelimuoto in ['t64', 't75', 't86']:
        vain_ylin = 2.5
    bets = []
    for yhd in kertoimet:
        y= tuple([int(y) for y in yhd['combination'].split('-')])
        if y in yhdistelmat:
            kerroin = vain_ylin * float(yhd.string.replace(',', '.')) / conf['panos']
            if int(kerroin) == 0:
                kerroin = metadata.jako / conf['panos'] # max kerroin jos yhdistelmää ei pelattu
            oma_kerroin = 1 / yhdistelma_tn(y, pros)
            yhdistelma = yhd['combination'].replace('-', '/')
            bet = bet_size(kerroin, oma_kerroin, yhdistelma, conf)
            if bet:
                bets.append(bet)
    write_to_file(bets, pelimuoto, args, metadata)


def t_peli_pros(args, prosentit, metadata, peliprosentit):
    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}: PROSENTIT')
    conf = get_data.get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(conf['lahtoja'])
    pros = {}
    for i in range(conf['lahtoja']):
        lahto = str(int(args.lahto) + i)
        lahto_t_peli = str(i + 1)
        pros[lahto_t_peli] = [p/100 for p in prosentit[lahto]]
        conf['L' + lahto_t_peli] = hajota.split_abcd(pros[lahto_t_peli], conf['rajat'])
    yhdistelmat = hajota.hajotus_rivit(conf)
    pelipros = {}
    for key in peliprosentit.keys():
        pelipros[key] = [p/100 for p in peliprosentit[key]]
    vain_ylin = 1
    bets = []
    for yhd in yhdistelmat:
        # vain ylin voittoluokka
        kerroin = (metadata.jako / metadata.vaihto) / yhdistelma_tn(yhd, pelipros)
        oma_kerroin = 1 / yhdistelma_tn(yhd, pros)
        yhdistelma = '/'.join([str(y) for y in yhd])
        bet = bet_size(kerroin, oma_kerroin, yhdistelma, conf)
        if bet:
            bets.append(bet)
    write_to_file(bets, pelimuoto, args, metadata)


def kelly(kerroin, oma_kerroin):
    kellyp = (kerroin - oma_kerroin) / (kerroin - 1) / oma_kerroin if kerroin > oma_kerroin else 0
    return kellyp


def bet_size(kerroin, oma_kerroin, yhd, conf):
    kellypr = kelly(kerroin, oma_kerroin)
    if conf['moninkertaistus']:
        kertaa = int(kellypr / conf['min_kelly'])
    else:
        kertaa = 1 if kellypr > conf['min_kelly'] else 0
    if kertaa * conf['panos'] * kerroin < conf['min_lunastus']:
        bet = None
    else:
        bet = Bet(
                yhdistelma=yhd.replace('-', '/'),
                kerroin=kerroin,
                oma_kerroin=oma_kerroin,
                pelipanos=kertaa*conf['panos']
                )
    return bet


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


def yhdistelma_tn(yhdistelma, prosentit):
    tn = []
    for tlahto, numero in enumerate(yhdistelma, 1):
        tn.append(prosentit[str(tlahto)][numero - 1])
    return prod(tn)
