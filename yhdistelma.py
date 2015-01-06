__author__ = 'kari'

def ok(yhd, systeemi):
    mini = systeemi[0][0]
    laskuri = 0
    oukkidoukki = False
    for l in range(1, len(yhd)+1):
        for m in range(0, len(systeemi[l])):
            if yhd[l-1] == systeemi[l][m]:
                laskuri += 1
    if laskuri >= mini:
        oukkidoukki = True

    return oukkidoukki

def tro_ok(yhd, systeemi):
    mini = systeemi[0][0]
    laskuri = 0
    oukkidoukki = False
    for l in range(0, 3):
        for m in range(0, len(systeemi[1])):
            if yhd[l] == systeemi[1][m]:
                laskuri += 1
        for n in range(0, len(systeemi[2])):
            if yhd[l] == systeemi[2][n]:
                laskuri = -10
    if laskuri >= mini:
        oukkidoukki = True

    return oukkidoukki
