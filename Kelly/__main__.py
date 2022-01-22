import argparse
import datetime
from decouple import config
import signal
import sys

from .analyysi import analysoi
from .get_data import excel_prosentit
from .bet_calc import peli
from .simulation import simulation
from .veikkaus import tanaan

PACKAGE_NAME = 'kelly'
PVM = datetime.datetime.now().strftime("%d%m%Y")



def register_exit_handler(func):
    signal.signal(signal.SIGTERM, func)


def sigterm_exit(_sig_func=None):
    sys.exit(0)


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
    parser_simu.set_defaults(func=simulation)

    parser_prosentit = subparser.add_parser('prosentit', help='Lue prosentit')
    parser_prosentit.add_argument('ratakoodi', help='Ratakoodi')
    parser_prosentit.set_defaults(func=excel_prosentit)

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
