import datetime
import os
from itertools import product

from .get_data import (get_json, get_prosentit, yhdistelma_tn, p_1,
                       Voittaja, Sija, Kaksari, Troikka, TPeli)
from . import hajota
from .veikkaus import hae_kertoimet, Tprosentit
from .validoi import troikka_yhdistelma_ok
from .util import write_to_file, otsikko

PELIT_FOLDER = os.environ['PELIT_FOLDER']
PROSENTIT_FOLDER = os.environ['PROSENTIT_FOLDER']
PVM = datetime.datetime.now().strftime("%y%m%d")


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
    otsikko(f'VOITTAJA  {args.ratakoodi} lähtö {args.lahto}  '
            f'(vaihto {metadata.vaihto})')
    print(f'  {"nro":>3}  {"kerroin":>8}  {"oma":>7}  {"kelly":>7}')
    voit = Voittaja(args.lahto, prosentit)
    for voittaja in kertoimet:
        num = int(voittaja['runner'])
        vkerr = float(voittaja.string.replace(',', '.'))
        okelly, oma_kerr = voit.kelly(num, vkerr)
        if okelly > 0.05:
            print(f'  {num:>3}  {vkerr:>8.1f}  {oma_kerr:>7.1f}  '
                  f'{100*okelly:>6.1f} %')


def sija(args, prosentit, metadata, kertoimet):
    otsikko(f'SIJA  {args.ratakoodi} lähtö {args.lahto}  '
            f'(vaihto {metadata.vaihto})')
    print(f'  {"nro":>3}  {"haarukka":>15}  {"oma":>7}')
    sij = Sija(args.lahto, prosentit)
    for sija in kertoimet:
        num = int(sija['runner'])
        yla = float(sija['high-probable'].replace(',', '.'))
        haar = sija['low-probable'] + ' - ' + sija['high-probable']
        oma_kerr = sij.oma_kerroin(num)
        if oma_kerr and oma_kerr < yla:
            print(f'  {num:>3}  {haar:>15}  {oma_kerr:>7.2f}')


def kaksari(args, prosentit, metadata, kertoimet):
    otsikko(f'KAKSARI  {args.ratakoodi} lähtö {args.lahto}  '
            f'(vaihto {metadata.vaihto})')
    print(f'  {"yhd.":>6}  {"kerroin":>8}  {"oma":>7}  {"kelly":>7}')
    kaks = Kaksari(args.lahto, prosentit)
    for kaksari in kertoimet:
        y = [int(y) for y in kaksari['combination'].split('-')]
        kkerr = float(kaksari.string.replace(',', '.'))
        okelly, omakk = kaks.kelly(y, kkerr)
        if okelly > 0.01:
            print(f'  {kaksari["combination"]:>6}  {kkerr:>8.1f}  '
                  f'{omakk:>7.1f}  {100*okelly:>6.1f} %')


def duo(args, prosentit, metadata, kertoimet):
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
    conf = get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(conf['lahtoja'])
    tpeli = TPeli(args.lahto, prosentit, conf)
    yhdistelmat = hajota.hajotus_rivit(conf)
    vain_ylin = 1
    if args.vain_ylin:
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
    conf = get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(conf['lahtoja'])
    tpeli = TPeli(args.lahto, prosentit, conf)
    for i in range(conf['lahtoja']):
        lahto = str(int(args.lahto) + i)
        lahto_t_peli = str(i + 1)
        # split_abcd luokittelee prosenttilistan (0..100) rajojen mukaan;
        # conf['rajat'] on samoissa prosenttiyksiköissä
        conf['L' + lahto_t_peli] = hajota.split_abcd(prosentit[lahto],
                                                     conf['rajat'])
    yhdistelmat = hajota.hajotus_rivit(conf)
    # peliprosentit avaimet ovat T-pelin sisäisiä lähtöindeksejä '1'..'N'
    pelipros = {}
    for key in peliprosentit.keys():
        pelipros[key] = p_1(peliprosentit[key])
    bets = []
    for yhd in yhdistelmat:
        # vain ylin voittoluokka
        kerroin = ((metadata.jako / metadata.vaihto)
                   / yhdistelma_tn(1, yhd, pelipros))
        bet = tpeli.bet_size(yhd, kerroin)
        if bet:
            bets.append(bet)
    write_to_file(bets, pelimuoto, args, metadata, huomio='  [prosentit]')
