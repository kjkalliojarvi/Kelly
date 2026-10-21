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
        total_rivit.update(rivit)
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
    limits = [
        ('A', rajat['A_to_B']),
        ('B', rajat['B_to_C']),
        ('C', rajat['C_to_D']),
        ('D', rajat['D_to_X'])
    ]
    for i, num in enumerate(prosentit, 1):
        for category, limit in limits:
            if num > limit:
                L[category].append(i)
                break
        else:
            L['X'].append(i)
    return L


def get_category(abcd, number):
    for kategoria in abcd:
        if number in abcd[kategoria]:
            return kategoria
