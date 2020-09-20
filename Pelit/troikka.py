# -*- coding: UTF-8 -*-
__author__ = 'kari'

import sys
import Prosentit
import kertoimet
import yhdistelma
import sijatn
import analyysi

systeemi = []
koodi = sys.argv[1]
lahto = sys.argv[2]
print 'Troikka: Ravit '+ koodi + ', Lähtö ' + lahto

pros = Prosentit.pros(koodi)
p1 = pros[int(lahto) - 1][:]
p2 = sijatn.toinen(p1)
p3 = sijatn.kolmas(p1)

paraf = open('troikka_para.txt')        
para = [float(x) for x in paraf.readline().split(',')]		# 0 = min Kelly, 1 = panos, 2 = min lunastus
								    # 0 = kuinka monta omaa systeemissä, 1 = hepot systeemissä, 2 = tappo hepot
for line in open('troikka.txt'):
    systeemi.append([int(x) for x in line.split(',')])

kerroinxml = kertoimet.bs(koodi, lahto, 'tro')

data = kerroinxml.find('pool')
vaihto = data['net-sales']
jako = data['net-pool']
lyhenne = kerroinxml.card['code']
pvm = kerroinxml.card['date'][0:5]
peli = data['type']

omatn = 0.0
lkm = 0
total = 0.0
minlunde = 100000.0
maxlunde = 0.0
avelunde = 0.0

out = open('/home/kari/Python/Pelit/troikka.peli', 'w')
for yhd in kerroinxml.find_all('probable'):
    y = [int(y) for y in yhd['combination'].split('-')]
    if yhdistelma.tro_ok(y, systeemi):
        kerroin = float(yhd.string.replace(',', '.'))
        if int(kerroin) == 0:
            kerroin = 2.0 * float(jako.replace(',', '.'))                  # max kerroin jos yhdistelmää ei pelattu
        omakerr = 100000.0
        if (p1[y[0] - 1] * p2[y[1] - 1] * p3[y[2] - 1]) > 0.000001:
            omakerr = ((1 - p2[y[0] - 1])*(1-p3[y[0] - 1]-p3[y[1] - 1])) / (p1[y[0] - 1]*p2[y[1] - 1]*p3[y[2] - 1])

        """print 'Kerroin ',
        print kerroin,
        print '  - ',
        print omakerr"""
        if kerroin > omakerr > 0:
            kelly = (kerroin - omakerr) / (kerroin - 1) / omakerr
            kert = int(kelly / para[0])
            lunde = kert * para[1] * kerroin
            if lunde > para[2]:
                lkm += 1
                omatn += 1 / omakerr
                total += kert * para[1]
                avelunde += lunde / omakerr
                if lunde < minlunde:
                    minlunde = lunde
                if lunde > maxlunde:
                    maxlunde = lunde
                txt = lyhenne + ';' + pvm + ';' + lahto + ';' + peli + ';' + yhd['combination'].replace('-', '/') + ';'
                ps = '{0:.1f}'.format(kert * para[1])
                print txt + ps + ';' + ps
                out.write(txt + ps + ';' + ps + '\n')


print 'Yht;' + str(lkm) + ';' + '{0:.1f}'.format(total)
out.write('Yht;' + str(lkm) + ';' + '{0:.1f}'.format(total))
print '<<<<<>>>>>'
tomatn = 0.0
if omatn > 0.0001:
    tomatn = total / omatn
print 'Oma todennäköisyys: ' + '{0:.1f}'.format(100*omatn) + ' % // ' + '{0:.1f}'.format(tomatn)
print 'Vaihto: ' + vaihto + ' / Jako: '+ jako
print 'Min: ' + '{0:.1f}'.format(minlunde) + ' / Average: ' + '{0:.1f}'.format(avelunde/omatn) + ' / Max: ' + '{0:.1f}'.format(maxlunde)
print '<<<<<>>>>>'
out.flush()
out.close()
analyysi.Analyysi('/home/kari/Python/Pelit/troikka.peli')
