# -*- coding: UTF-8 -*-
__author__ = 'kari'

import sys
import Prosentit
import kertoimet
import yhdistelma
import sijatn
import analyysi

ratakoodi = sys.argv[1]
kerroinkoodi = sys.argv[2]
lahto = sys.argv[3]
print 'Voittaja-Sija-Kaksari: Ravit: ' + ratakoodi + ' Lähtö: ' + lahto

pros = Prosentit.pros(ratakoodi)
p1 = pros[int(lahto) - 1][:]
p2 = sijatn.toinen(p1)
p3 = sijatn.kolmas(p1)  

voittajaxml = kertoimet.bs(ratakoodi, lahto, 'voi')
sijaxml = kertoimet.bs(ratakoodi,lahto,'sij')
kaksarixml = kertoimet.bs(ratakoodi, lahto, 'kak')

voidata = voittajaxml.find('pool')
voivaihto = voidata['net-sales']
voijako = voidata['net-pool']

sijdata = sijaxml.find('pool')
sijvaihto = sijdata['net-sales']
sijjako = sijdata['net-pool']

kakdata = kaksarixml.find('pool')
kakvaihto = kakdata['net-sales']
kakjako = kakdata['net-pool']

print 'Voittaja:'
for voittaja in voittajaxml.find_all('probable'):
    num = int(voittaja['runner'])
    vkerr = float(voittaja.string.replace(',', '.'))
    omavk = 1000
    if p1[num-1] > 0:
        omavk = 1 / p1[num-1]
    if vkerr > omavk:
        kelly = (vkerr - omavk) / (vkerr - 1) / omavk
        if kelly > 0.05:
            print str(num) + ': ' + '{0:.1f}'.format(vkerr) + ' / ' + '{0:.1f}'.format(omavk) + ' / ' + '{0:.1f}'.format(100*kelly) + ' %'
         
print '----- * -----'
print 'Sija:'
for sija in sijaxml.find_all('probable'):
    num = int(sija['runner'])
    ala = float(sija['low-probable'].replace(',','.'))
    yla = float(sija['high-probable'].replace(',','.'))
    haar = sija['low-probable'] + ' - ' + sija['high-probable']
    sijap = p1[num-1] + p2[num-1] + p3[num-1]
    if sijap > .2:
        if 1/sijap < yla:
            print str(num) + ': ' + haar + ' / ' + '{0:.2f}'.format(1/sijap)
print '----- * -----'
print 'Kaksari:'
for kaksari in kaksarixml.find_all('probable'):
    y = [int(y) for y in kaksari['combination'].split('-')]
    kkerr = float(kaksari.string.replace(',', '.'))
    omakk = 100000.0
    if (p1[y[0] - 1] * p2[y[1] - 1]) > .000001:
        omakk = 1 / ( p1[y[0]-1]*p2[y[1]-1]/(1-p2[y[0]-1]) + p1[y[1]-1]*p2[y[0]-1]/(1-p2[y[1]-1]));
    if kkerr > omakk:
        kelly = (kkerr - omakk) / (kkerr - 1) / omakk
        if kelly > 0.01:
            print kaksari['combination']+': '+'{0:.1f}'.format(kkerr)+' / '+'{0:.1f}'.format(omakk)+' / '+'{0:.1f}'.format(100*kelly)+' %'
print '----- * -----'

