# -*- coding: UTF-8 -*-
__author__ = 'kari'

import urllib
from bs4 import BeautifulSoup
import datetime
import Prosentit
import sys

cards = urllib.urlopen('https://www.fintoto.fi/xml/cards.xml').read()
soup = BeautifulSoup(cards, 'xml')
pvm = datetime.datetime.now().strftime('%d.%m.%Y')
pvm2 = datetime.datetime.now().strftime('%d%m%Y')
p = [[0 for j in xrange(16)] for i in xrange(13)]
Hepot = [[] for i in xrange(13)]

koodi = sys.argv[1]

rr = '/home/kari/Python/Prosentit/'+koodi + '_' + pvm2+'.txt'
pr = open(rr)
pl = pr.readlines()
for line in pl:
    v = line.split(',')
    i = 0
    j = 0
    for a in v:
        if a[0] == 'R':
            i = int(a[1:])
        else:
            p[i-1][j] = int(a)
            j += 1

Lahtoja=0
for ravit in soup.find_all('card'):
    if ravit['date'] == pvm and ravit['track-code'] == koodi:
        for n in ravit.find_all('race'):
            i = int(n['number'])
            if i > Lahtoja:
                Lahtoja = i            
            Hepot[i-1].append(int(n.runners.string))
            if n.runners.has_attr('scratched'):
               pois = n.runners['scratched']
               v = pois.split(',')
               for poro in v:
                   Hepot[i-1].append(int(poro))

for i in range(0, Lahtoja):
    summa = 0
    for j in range(0, Hepot[i][0]):
        summa += p[i][j]

    if summa > 0:
        print('Lähtö ' + str(i+1) + ' : '),
        print(p[i][:])
        if summa != 100:
            print '     Prosenttien summa ei ole 100 (' + str(summa) +')'
        for j in range(1, len(Hepot[i])):
            if p[i][Hepot[i][j]-1] > 0:
                print '     Numero ' + str(Hepot[i][j]) + ' on poissa!!!'
