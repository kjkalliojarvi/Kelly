import argparse
import datetime
import os
import signal
import sys

from . import get_data
from .Kelly import voittaja, sija, kaksari, duo, troikka, t_peli

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
    prosentti_file = args.ratakoodi + '_' + PVM + '.json'
    prosentit = get_data.prosentit(PROSENTIT_FOLDER + prosentti_file)
    metadata, kertoimet = get_data.kertoimet(args.ratakoodi,
                                             args.lahto,
                                             args.pelimuoto)
    kutsu = {'voi': voittaja, 'sij': sija, 'kak': kaksari,
             'tro': troikka, 'duo': duo, 't4': t_peli,
             't5': t_peli, 't6': t_peli, 't7': t_peli,
             't8': t_peli}
    kutsu[args.pelimuoto](args, prosentit, metadata, kertoimet)


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
    parser_peli.add_argument('pelimuoto', help='Pelimuoti',
                             choices=['voi', 'sij', 'kak', 'duo', 'tro', 't4',
                                      't5', 't6', 't7', 't8'])
    parser_peli.add_argument('-y', '--vain_ylin',
                             help='Vain ylin voittoluokka',
                             default=True)
    parser_peli.set_defaults(func=peli)

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
