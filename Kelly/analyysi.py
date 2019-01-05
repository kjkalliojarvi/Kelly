# -*- coding: UTF-8 -*-
__author__ = 'kari'

def Analyysi(pelifile):
    pelif = open(pelifile)
    rivi = []
    rivi0 = pelif.readline().split(';')
    rivi = [int(x) for x in rivi0[4].split('/')]
    panos = float(rivi0[5])
    peli = {'DUO': 2, 'TRO': 3, 'T4': 4, 'T5': 5, 'T6': 6, 'T65': 6, 'T7': 7,  'T75': 7}
    l = peli[rivi0[3]]
    laskuri = [[0 for i in range(16)] for j in range(l)]
    kokpanos = [[0.0 for i in range(16)] for j in range(l)]
    riveja = 0
    total = 0.0
    while True:
        for ll in range(l):
            #print ll
            laskuri[ll][rivi[ll]] += 1
            kokpanos[ll][rivi[ll]] += panos
        rivi0 = pelif.readline().split(';')
        if rivi0[0] == 'Yht':
            riveja = rivi0[1]
            total = rivi0[2]
            break
        else:
            rivi = [int(x) for x in rivi0[4].split('/')]
            panos = float(rivi0[5])
    print 'Rastit' + str(riveja)
    for i in range(16):
        print '{0:3d} |'.format(i+1),
    print ''
    for i in range(16):
        print '=====',
    print ''
    for ll in range(l):
        for h in range(16):
            print '{0:3d} |'.format(laskuri[ll][h]),
        print ''
    print 'Rastit ' 
    a = 0
    for i in range(16):
        print '{0:3d} |'.format(i+1),
    print ''
    for i in range(16):
        print '==== ',
    print ''
    for ll in range(l):
        a = 0
        for h in range(16):
            print '{0:3d} |'.format(laskuri[ll][h]),
            a += laskuri[ll][h]
        print a
    print '%-osuudet'
    for i in range(16):
        print '{0:3d} |'.format(i+1),
    print ''
    for i in range(16):
        print '=====',
    print ''
    for ll in range(l):
        for h in range(16):
            print '{0:3.0f} |'.format(100*float(laskuri[ll][h])/float(riveja)),
        print ''
    print '%-osuudet rahasta'
    for i in range(16):
        print '{0:3d} |'.format(i+1),
    print ''
    for i in range(16):
        print '=====',
    print ''
    for ll in range(l):
        for h in range(16):
            print '{0:3.0f} |'.format(100*float(kokpanos[ll][h])/float(total)),
        print ''
    
