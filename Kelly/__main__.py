import argparse
import signal
import sys

from . import __version__
from .analyysi import analysoi
from .get_data import excel_prosentit
from .bet_calc import peli
from .simulation import simulation
from .veikkaus import tanaan

PACKAGE_NAME = 'kelly'

# Pool-type codes. The single-race pools plus the multi-leg T-pools are valid
# for `peli`; only the T-pools can be simulated.
YKSITTAISPELIT = ['voi', 'sij', 'kak', 'duo', 'tro']
T_PELIT = ['t4', 't5', 't64', 't65', 't75', 't85', 't86']
PELIMUODOT = YKSITTAISPELIT + T_PELIT


def register_exit_handler(func):
    signal.signal(signal.SIGTERM, func)


def sigterm_exit(_sig_func=None):
    sys.exit(0)


def _add_tanaan_parser(subparser):
    parser_tanaan = subparser.add_parser(
        'tanaan', help='Listaa tämän päivän ravit Veikkauksen rajapinnasta')
    parser_tanaan.set_defaults(func=tanaan)


def _add_prosentit_parser(subparser):
    parser_prosentit = subparser.add_parser(
        'prosentit',
        help='Lue prosentit.xlsx ja kirjoita radan todennäköisyys-JSON')
    parser_prosentit.add_argument('ratakoodi', help='Radan koodi, esim. H')
    parser_prosentit.set_defaults(func=excel_prosentit)


def _add_peli_parser(subparser):
    parser_peli = subparser.add_parser(
        'peli', help='Laske Kelly-panokset yhdelle pelimuodolle')
    parser_peli.add_argument('ratakoodi', help='Radan koodi, esim. H')
    parser_peli.add_argument('lahto', help='Lähdön numero')
    parser_peli.add_argument('pelimuoto', choices=PELIMUODOT,
                             metavar='pelimuoto',
                             help='Pelimuoto: %(choices)s')
    parser_peli.add_argument('--prosentit', default=False, action='store_true',
                             help='Käytä poolin toteutuneita pelimääriä '
                                  'kertoimien sijaan')
    parser_peli.add_argument('-y', '--vain-ylin', dest='vain_ylin',
                             default=True,
                             action=argparse.BooleanOptionalAction,
                             help='Huomioi vain ylin voittoluokka '
                                  'T-peleissä (oletus: kyllä). --no-vain-ylin '
                                  'poistaa voittoluokkakertoimen')
    parser_peli.set_defaults(func=peli)


def _add_simu_parser(subparser):
    parser_simu = subparser.add_parser(
        'simu', help='Monte Carlo -simulaatio T-pelin hajotukselle')
    parser_simu.add_argument('ratakoodi', help='Radan koodi, esim. H')
    parser_simu.add_argument('lahto', help='Lähdön numero')
    parser_simu.add_argument('pelimuoto', choices=T_PELIT,
                             metavar='pelimuoto',
                             help='T-pelimuoto: %(choices)s')
    parser_simu.set_defaults(func=simulation)


def _add_analyysi_parser(subparser):
    parser_analyysi = subparser.add_parser(
        'analyysi', help='Analysoi valmis .peli-tiedosto (ristiintaulukointi)')
    parser_analyysi.add_argument('pelimuoto_', metavar='pelimuoto',
                                 choices=['duo', 'troikka', 't4', 't5', 't6',
                                          't7', 't8'],
                                 help='Pelimuoto: %(choices)s')
    parser_analyysi.set_defaults(func=analysoi)


def build_parser():
    parser = argparse.ArgumentParser(
        prog=PACKAGE_NAME,
        description='Kelly-kriteerin panostuslaskuri Veikkauksen '
                    'totopeleille.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Esimerkkejä:\n'
            '  kelly tanaan\n'
            '  kelly prosentit H\n'
            '  kelly peli H 3 voi\n'
            '  kelly peli H 1 t65 --prosentit\n'
            '  kelly simu H 1 t65\n'
            '  kelly analyysi t65\n'
        ),
    )
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__}')

    subparser = parser.add_subparsers(title='Komennot', dest='command',
                                      metavar='<komento>')

    _add_tanaan_parser(subparser)
    _add_prosentit_parser(subparser)
    _add_peli_parser(subparser)
    _add_simu_parser(subparser)
    _add_analyysi_parser(subparser)

    return parser


def kelly():
    register_exit_handler(sigterm_exit)

    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sigterm_exit(None)

    try:
        args.func(args)
    except (KeyboardInterrupt, SystemExit):
        sigterm_exit(None)


if __name__ == '__main__':
    kelly()
