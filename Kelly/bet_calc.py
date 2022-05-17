import datetime
from decouple import config
from itertools import product

from .get_data import (get_json, get_prosentit, yhdistelma_tn, p_1,
                       Voittaja, Sija, Kaksari, Troikka, TPeli)
from . import hajota
from .veikkaus import hae_kertoimet, Tprosentit
from .validoi import troikka_yhdistelma_ok
from .util import write_to_file

PELIT_FOLDER = config('PELIT_FOLDER')
PROSENTIT_FOLDER = config('PROSENTIT_FOLDER')
PVM = datetime.datetime.now().strftime("%d%m%Y")


def peli(args):
    filename = f'{PROSENTIT_FOLDER}{args.ratakoodi}_{PVM}.json'
    prosentit = get_prosentit(filename)
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
    print(f'Voittaja: Lähtö {args.lahto}, vaihto {metadata.vaihto}')
    voit = Voittaja(args.lahto, prosentit)
    for voittaja in kertoimet:
        num = int(voittaja['runner'])
        vkerr = float(voittaja.string.replace(',', '.'))
        okelly, oma_kerr = voit.kelly(num, vkerr)
        if okelly > 0.05:
            print(f'{num:2}: {vkerr:3.1f} / {oma_kerr:3.1f} / {100*okelly:3.1f} %')
    print('----- * -----')


def sija(args, prosentit, metadata, kertoimet):
    print(f'Sija: Lähtö {args.lahto}, vaihto {metadata.vaihto}')
    sij = Sija(args.lahto, prosentit)
    for sija in kertoimet:
        num = int(sija['runner'])
        yla = float(sija['high-probable'].replace(',', '.'))
        haar = sija['low-probable'] + ' - ' + sija['high-probable']
        oma_kerr = sij.oma_kerroin(num)
        if oma_kerr and oma_kerr < yla:
            print(f'{num:2}: {haar} / {oma_kerr:2.2f}')
    print('----- * -----')


def kaksari(args, prosentit, metadata, kertoimet):
    print(f'Kaksari: Lähtö {args.lahto}, vaihto {metadata.vaihto}')
    kaks = Kaksari(args.lahto, prosentit)
    for kaksari in kertoimet:
        y = [int(y) for y in kaksari['combination'].split('-')]
        kkerr = float(kaksari.string.replace(',', '.'))
        okelly, omakk = kaks.kelly(y, kkerr)
        if okelly > 0.01:
            print(f'{kaksari["combination"]:>5}: '
                  f'{kkerr:5.1f} / {omakk:4.1f} / {100*okelly:4.1f} %')
    print('----- * -----')


def duo(args, prosentit, metadata, kertoimet):
    print(f'Duo: Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    conf = get_json(PELIT_FOLDER + 'duo.json')
    duopeli = TPeli(args.lahto, prosentit, conf)
    yhdistelmat = list(product(conf['L1'], conf['L2']))
    bets = []
    for yhd in kertoimet:
        y = tuple([int(y) for y in yhd['combination'].split('-')])
        if y in yhdistelmat:
            kerroin = float(yhd.string.replace(',', '.'))
            if int(kerroin) == 0:
                kerroin = metadata.jako  # max kerroin jos yhdistelmää ei pelattu
            bet = duopeli.bet_size(y, kerroin)
            if bet:
                bets.append(bet)
    write_to_file(bets, 'duo', args, metadata)


def troikka(args, prosentit, metadata, kertoimet):
    print(f'Troikka: Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    conf = get_json(PELIT_FOLDER + 'troikka.json')
    tro = Troikka(args.lahto, prosentit, conf)
    bets = []
    for yhd in kertoimet:
        y = [int(y) for y in yhd['combination'].split('-')]
        if troikka_yhdistelma_ok(y, conf):
            kerroin = float(yhd.string.replace(',', '.'))
            if int(kerroin) == 0:
                kerroin = 2.0 * metadata.jako  # max kerroin jos yhdistelmää ei pelattu
            bet = tro.bet_size(y, kerroin)
            if bet:
                bets.append(bet)
    write_to_file(bets, 'tro', args, metadata)


def t_peli(args, prosentit, metadata, kertoimet):
    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    conf = get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(conf['lahtoja'])
    tpeli = TPeli(args.lahto, prosentit, conf)
    yhdistelmat = hajota.hajotus_rivit(conf)
    vain_ylin = 1
    if args.pelimuoto in ['t65']:
        vain_ylin = 2
    if args.pelimuoto in ['t64', 't75', 't86']:
        vain_ylin = 2.5
    bets = []
    for yhd in kertoimet:
        y = tuple([int(y) for y in yhd['combination'].split('-')])
        if y in yhdistelmat:
            kerroin = vain_ylin * float(yhd.string.replace(',', '.')) / conf['panos']
            if int(kerroin) == 0:
                kerroin = metadata.jako / conf['panos'] # max kerroin jos yhdistelmää ei pelattu
            bet = tpeli.bet_size(y, kerroin)
            if bet:
                bets.append(bet)
    write_to_file(bets, pelimuoto, args, metadata)


def t_peli_pros(args, prosentit, metadata, peliprosentit):
    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}: PROSENTIT')
    conf = get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(conf['lahtoja'])
    tpeli = TPeli(args.lahto, prosentit, conf)
    pros = {}
    for i in range(conf['lahtoja']):
        lahto = str(int(args.lahto) + i)
        lahto_t_peli = str(i + 1)
        pros[lahto_t_peli] = p_1(prosentit[lahto])
        conf['L' + lahto_t_peli] = hajota.split_abcd(pros[lahto_t_peli], conf['rajat'])
    yhdistelmat = hajota.hajotus_rivit(conf)
    pelipros = {}
    for key in peliprosentit.keys():
        pelipros[key] = p_1(peliprosentit[key])
    bets = []
    for yhd in yhdistelmat:
        # vain ylin voittoluokka
        kerroin = (metadata.jako / metadata.vaihto) / yhdistelma_tn(yhd, pelipros)
        yhdistelma = '/'.join([str(y) for y in yhd])
        bet = tpeli.bet_size(yhdistelma, kerroin)
        if bet:
            bets.append(bet)
    write_to_file(bets, pelimuoto, args, metadata)
