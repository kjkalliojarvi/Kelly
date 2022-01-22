import json
from decouple import config
import datetime
from collections import namedtuple
import sys
from openpyxl import load_workbook

from .validoi import tarkista_prosentit


PROSENTIT_FOLDER = config('PROSENTIT_FOLDER')
PVM = datetime.datetime.now().strftime("%d%m%Y")


def get_json(filename):
    try:
        with open(filename, 'r') as rawfile:
            jsonfile = json.loads(rawfile.read())
    except FileNotFoundError:
        print(f'Ei fileä: {filename}')
        sys.exit(1)
    return jsonfile


def prosentit(filename):
    prosentit = get_json(filename)
    tarkista_prosentit(prosentit, filename)
    return prosentit


def excel_prosentit(args):
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
