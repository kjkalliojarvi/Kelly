import argparse
import datetime
import json
from openpyxl import load_workbook
import os
import signal
import sys

from . import get_data
from .bet_calc import voittaja, sija, kaksari, duo, troikka, t_peli, t_peli_pros
from .simulation import t_peli_simu

PACKAGE_NAME = 'kelly'
PVM = datetime.datetime.now().strftime("%d%m%Y")
PROSENTIT_FOLDER = os.environ['PROSENTIT_FOLDER']


def register_exit_handler(func):
    signal.signal(signal.SIGTERM, func)


def sigterm_exit(_sig_func=None):
    sys.exit(0)


def tanaan(args):
    pvm = datetime.datetime.now().strftime('%d.%m.%Y')
    for ravit in get_data.listat():
        if ravit['date'] == pvm:
            a = ravit.find('pool')['file'].split('_')
            print(ravit['name'], ravit['code'], ravit['track-code'], a[0])


def peli(args):
    url = f'{PROSENTIT_FOLDER}{args.ratakoodi}_{PVM}.json'
    prosentit = get_data.prosentit(url)
    if args.pelimuoto in ['voi', 'sij', 'kak', 'duo', 'tro']:
        kutsu = {'voi': voittaja, 'sij': sija, 'kak': kaksari,
                 'tro': troikka, 'duo': duo}
        metadata, kertoimet = get_data.kertoimet(args.ratakoodi,
                                                 args.lahto,
                                                 args.pelimuoto)
        kutsu[args.pelimuoto](args, prosentit, metadata, kertoimet)
    if args.pelimuoto in ['t4', 't5', 't64', 't65', 't75', 't86']:
        if args.prosentit:
            metadata, peliprosentit = get_data.Tprosentit(args.ratakoodi,
                                                          args.lahto,
                                                          args.pelimuoto)
            t_peli_pros(args, prosentit, metadata, peliprosentit)
        else:
            metadata, kertoimet = get_data.kertoimet(args.ratakoodi,
                                                     args.lahto,
                                                     args.pelimuoto,
                                                     compressed=True)
            t_peli(args, prosentit, metadata, kertoimet)


def analysoi(args):
    get_data.analyysi(args.pelimuoto_)


def simu(args):
    if args.pelimuoto in ['t4', 't5', 't64', 't65', 't75', 't86']:
        metadata, peliprosentit = get_data.Tprosentit(args.ratakoodi,
                                                      args.lahto,
                                                      args.pelimuoto)
        t_peli_simu(args, peliprosentit)


def prosentit(args):
    wb = load_workbook(f'{PROSENTIT_FOLDER}prosentit.xlsx', data_only=True)
    pros = wb['Prosentit']
    row = 2
    columns = 'BCDEFGHIJKLMNOPQ'
    prosentti = {}
    while pros[f'R{row}'].value is not None:
        p = []
        key = str(row - 1)
        if pros[f'R{row}'].value == 100:
            for column in columns:
                if pros[f'{column}{row}'].value is not None:
                    p.append(pros[f'{column}{row}'].value)
            prosentti[key] = p
        row += 1
    filename = f'{PROSENTIT_FOLDER}{args.ratakoodi}_{PVM}.json'
    with open(filename, 'w') as jsonfile:
        json.dump(prosentti, jsonfile)


def kelly():
    register_exit_handler(sigterm_exit)

    sys.argv[0] = PACKAGE_NAME
    parser = argparse.ArgumentParser(description='Kelly betting')

    subparser = parser.add_subparsers(title='Commands', dest='command')

    parser_tanaan = subparser.add_parser('tanaan', help='Ravit tänään')
    parser_tanaan.set_defaults(func=tanaan)

    parser_peli = subparser.add_parser('peli', help='Peli')
    parser_peli.add_argument('ratakoodi', help='Ratakoodi')
    parser_peli.add_argument('lahto', help='lahto')
    parser_peli.add_argument('pelimuoto', help='Pelimuoto',
                             choices=['voi', 'sij', 'kak', 'duo', 'tro', 't4',
                                      't5', 't64', 't65', 't75', 't86'])
    parser_peli.add_argument('--prosentit', help='Käytä prosentteja',
                             default=False, action='store_true')
    parser_peli.add_argument('-y', '--vain_ylin',
                             help='Vain ylin voittoluokka',
                             default=True)
    parser_peli.set_defaults(func=peli)

    parser_analyysi = subparser.add_parser('analyysi', help='analyysi')
    parser_analyysi.add_argument('pelimuoto_', help='Pelimuoto',
                                 choices=['duo', 'troikka', 't4', 't5', 't6', 't7', 't8'])
    parser_analyysi.set_defaults(func=analysoi)

    parser_simu = subparser.add_parser('simu', help='T-peli simulaatio')
    parser_simu.add_argument('ratakoodi', help='Ratakoodi')
    parser_simu.add_argument('lahto', help='lahto')
    parser_simu.add_argument('pelimuoto', help='Pelimuoto',
                             choices=['t4', 't5', 't64', 't65', 't75', 't86'])
    parser_simu.set_defaults(func=simu)

    parser_prosentit = subparser.add_parser('prosentit', help='Lue prosentit')
    parser_prosentit.add_argument('ratakoodi', help='Ratakoodi')
    parser_prosentit.set_defaults(func=prosentit)

    args, _ = parser.parse_known_args()
    if not args.command:
        parser.print_help()
        sigterm_exit(None)

    try:
        args.func(args)
    except (KeyboardInterrupt, SystemExit):
        sigterm_exit(None)


if __name__ == '__main__':
    kelly()
