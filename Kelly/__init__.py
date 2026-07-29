# -*- coding: utf-8 -*-

"""Top-level package for Kelly."""

import os
import sys

from dotenv import find_dotenv, load_dotenv

# Load .env into the process environment once, before any submodule reads it.
load_dotenv(find_dotenv(usecwd=True))

# Submodules read these at import time, so fail early with a clear message
# instead of a raw KeyError traceback deep in an import chain.
_REQUIRED_ENV = ('PELIT_FOLDER', 'PROSENTIT_FOLDER')
_missing = [name for name in _REQUIRED_ENV if not os.environ.get(name)]
if _missing:
    sys.exit(
        'Kelly: puuttuvat ympäristömuuttujat: ' + ', '.join(_missing) + '.\n'
        'Aseta ne .env-tiedostossa tai ympäristössä ennen ajoa '
        '(katso CLAUDE.md / README).'
    )

__author__ = """kk"""
__email__ = 'kari.kalliojarvi@kolumbus.fi'
__version__ = '0.6.0'
