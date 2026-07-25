# -*- coding: utf-8 -*-

"""Top-level package for Kelly."""

from dotenv import find_dotenv, load_dotenv

# Load .env into the process environment once, before any submodule reads it.
load_dotenv(find_dotenv(usecwd=True))

__author__ = """kk"""
__email__ = 'kari.kalliojarvi@kolumbus.fi'
__version__ = '0.5.0'
