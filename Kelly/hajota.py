from more_itertools import distinct_permutations
from itertools import product


def hajotus_rivit(systeemi):
    """
    In:
        systeemi:  T-pelin tiedot
    Out:
        rivit:     hajotusten mukaiset rivit systeemistä
    """
    total_rivit = set()
    for hajotus in systeemi['hajotus']:
        rivit = rivit_abcd(hajotus, systeemi)
        total_rivit = set.union(total_rivit, rivit)
    return total_rivit


def rivit_abcd(abcd, systeemi):
    """
    Palauttaa rivit annetulle hajotukselle abcd
    """
    rivit = set()
    for permutation in distinct_permutations(abcd):
        perm_yhd = []
        for lahto, kategoria in enumerate(permutation, 1):
            perm_yhd.append(systeemi['L' + str(lahto)][kategoria])
        for rivi in product(*perm_yhd):
            rivit.add(rivi)
    return rivit


def split_abcd(prosentit, rajat):
    """
    Jakaa lähdön prosentit ABCD:hen
    """
    L = {'A': [], 'B': [], 'C': [], 'D': [], 'X': []}
    for i, num in enumerate(prosentit, 1):
        if num > rajat['A_to_B']:
            L['A'].append(i)
        elif num > rajat['B_to_C']:
            L['B'].append(i)
        elif num > rajat['C_to_D']:
            L['C'].append(i)
        elif num > rajat['D_to_X']:
            L['D'].append(i)
        else:
            L['X'].append(i)
    return L


def get_category(abcd, number):
    for kategoria in abcd:
        if number in abcd[kategoria]:
            return kategoria
