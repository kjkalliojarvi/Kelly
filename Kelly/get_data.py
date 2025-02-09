import json
import string
from decouple import config
import datetime
from collections import namedtuple
from dataclasses import dataclass, field
import sys
from math import prod
from openpyxl import load_workbook

from .validoi import tarkista_prosentit, troikka_yhdistelma_ok


PROSENTIT_FOLDER = config('PROSENTIT_FOLDER')
PVM = datetime.datetime.now().strftime("%y%m%d")
Bet = namedtuple('Bet', ['yhdistelma', 'kerroin', 'oma_kerroin', 'pelipanos'])


def get_json(filename):
    try:
        with open(filename, 'r') as rawfile:
            jsonfile = json.loads(rawfile.read())
    except FileNotFoundError:
        print(f'Ei fileä: {filename}')
        sys.exit(1)
    return jsonfile


def get_prosentit(filename):
    prosentit = get_json(filename)
    tarkista_prosentit(prosentit, filename)
    return prosentit


def p_1(p):
    return {ind: prob/100 for ind, prob in enumerate(p, 1)}


def p_2(p):
    kaksip = [0.0, 2.0, 4.2, 6.2, 8.0, 8.7, 9.6, 10.1, 11.2, 12.1,
              12.8, 13.7, 14.4, 15.0, 15.6, 16.0, 16.4, 16.7, 17.2, 17.7,
              18.0, 18.4, 18.55, 18.85, 19.0, 19.35, 19.35, 19.5, 19.3, 19.2,
              19.1, 19.0, 19.0, 19.0, 18.95, 18.9, 18.8, 18.7, 18.6, 18.6,
              18.5, 18.4, 18.3, 18.2, 18.1, 18.0, 17.85, 17.75, 17.5, 17.3,
              17.0, 16.9, 16.75, 16.6, 16.2, 15.8, 15.5, 15.3, 15.15, 14.9,
              14.5, 14.0, 13.55, 13.0, 12.6, 12.0, 11.4, 10.8, 10.2, 9.6,
              9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0]
    p2 = [kaksip[i] for i in p]
    return {ind: prob/sum(p2) for ind, prob in enumerate(p2, 1)}


def p_3(p):
    kolmep = [0.0, 4.0, 6.5, 8.6, 9.5, 10.7, 11.2, 11.6, 12.0, 12.3,
              12.5, 12.8, 13.0, 13.2, 13.3, 13.3, 13.2, 13.1, 13.0, 12.9,
              12.8, 12.7, 12.65, 12.55, 12.5, 12.35, 12.25, 12.2, 12.1, 12.0,
              11.9, 11.8, 11.7, 11.6, 11.55, 11.5, 11.3, 11.1, 11.0, 10.9,
              10.8, 10.6, 10.3, 10.0, 9.8, 9.6, 9.45, 9.25, 9.0, 8.8,
              8.6, 8.4, 8.25, 8.1, 8.0, 7.9, 7.8, 7.7, 7.55, 7.4,
              7.2, 7.0, 6.95, 6.8, 6.7, 6.6, 6.5, 6.4, 6.3, 6.2,
              6.1, 5.9, 5.7, 5.5, 5.3, 5.1, 4.9, 4.7, 4.5, 4.3, 4.1]
    p3 = [kolmep[i] for i in p]
    return {ind: prob/sum(p3) for ind, prob in enumerate(p3, 1)}


def multi_prosentit(lahto, lahtoja, prosentit):
    p = {}
    for i in range(lahtoja):
        l = f'{int(lahto)+i}'
        p[l] = p_1(prosentit[l])
    return p


def yhdistelma_tn(lahto, yhdistelma, prosentit):
    tn = []
    for tlahto, numero in enumerate(yhdistelma, int(lahto)):
        tn.append(prosentit[str(tlahto)][numero])
    return prod(tn)


def kelly_calc(kerroin, oma_kerroin):
    kellyp = (kerroin - oma_kerroin) / (kerroin - 1) / oma_kerroin if kerroin > oma_kerroin else 0
    return kellyp


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


@dataclass
class Peli:
    lahto: str
    prosentit: dict
    conf: dict = None
    p1: dict = field(init=False)
    p2: dict = field(init=False)
    p3: dict = field(init=False)

    def __post_init__(self):
        self.p1 = p_1(self.prosentit[self.lahto])
        self.p2 = p_2(self.prosentit[self.lahto])
        self.p3 = p_3(self.prosentit[self.lahto])

    def oma_kerroin(self, peli):
        pass

    def kelly(self, peli, kerroin):
        okelly = 0
        oma_kerr = self.oma_kerroin(peli)
        if oma_kerr:
            okelly = kelly_calc(kerroin, oma_kerr)
        return okelly, oma_kerr

    def bet_size(self, peli, kerroin):
        kellypr, oma_kerroin = self.kelly(peli, kerroin)
        if self.conf['moninkertaistus']:
            kertaa = int(kellypr / self.conf['min_kelly'])
        else:
            kertaa = 1 if kellypr > self.conf['min_kelly'] else 0
        if kertaa * self.conf['panos'] * kerroin < self.conf['min_lunastus']:
            bet = None
        else:
            bet = Bet(
                    yhdistelma='/'.join([str(y) for y in peli]),
                    kerroin=kerroin,
                    oma_kerroin=oma_kerroin,
                    pelipanos=kertaa*self.conf['panos']
                    )
        return bet


@dataclass
class Voittaja(Peli):
    def oma_kerroin(self, peli):
        return 1 / self.p1[peli] if self.p1[peli] else None


@dataclass
class Sija(Peli):
    def oma_kerroin(self, peli):
        sijap = self.p1[peli] + self.p2[peli] + self.p3[peli]
        return 1 / sijap if sijap else None


@dataclass
class Kaksari(Peli):
    def oma_kerroin(self, peli):
        y = peli
        return 1 / (self.p1[y[0]]*self.p2[y[1]]/(1-self.p2[y[0]]) + self.p1[y[1]]*self.p2[y[0]]/(1-self.p2[y[1]])) if (self.p1[y[0]]*self.p2[y[1]]) else None


@dataclass
class Troikka(Peli):
    def oma_kerroin(self, peli):
        y = peli
        return ((1 - self.p2[y[0]])*(1-self.p3[y[0]]-self.p3[y[1]])) / (self.p1[y[0]]*self.p2[y[1]]*self.p3[y[2]]) if (self.p1[y[0]]*self.p2[y[1]]*self.p3[y[2]]) else None


@dataclass
class TPeli(Peli):
    p: dict = field(init=False)

    def __post_init__(self):
        self.p = multi_prosentit(self.lahto, self.conf['lahtoja'], self.prosentit)

    def oma_kerroin(self, peli):
        return 1 / yhdistelma_tn(self.lahto, peli, self.p)
