# -*- coding: UTF-8 -*-
__author__ = 'kari'

import sys
import os
import Prosentit
import Tkertoimet
import yhdistelma
import Check
import analyysi

systeemi = []
koodi = sys.argv[1]
lahto = sys.argv[2]
print 'T4: Ravit '+ koodi + ', Lähtö ' + lahto + ' => '

l = int(lahto)
pros = Prosentit.pros(koodi)
p1 = pros[l - 1][:]
p2 = pros[l][:]
p3 = pros[l + 1][:]
p4 = pros[l + 2][:]

paraf = open('t4_para.txt')
				 # 0 = min Kelly, 1 = panos, 2 = min lunastus
para = [float(x) for x in paraf.readline().split(',')]

for line in open('t4.txt'):
    systeemi.append([int(x) for x in line.split(',')])

kerroinxml = Tkertoimet.bs(koodi, lahto, 't4')

data = kerroinxml.find('pool')
vaihto = float(data['net-sales'].replace(',','.'))
jako = float(data['net-pool'].replace(',','.'))
lyhenne = kerroinxml.card['code']
pvm = kerroinxml.card['date'][0:5]
peli = data['type']

rivit = {}
omatn = 0.0
lkm = 0
total = 0.0
minlunde = 100000.0
maxlunde = 0.0
avelunde = 0.0
                                            # luetaan data dictionaryyn
for yhd in kerroinxml.find_all('probable'):
    rivit[yhd['combination']] = {'pelattu': float(yhd['amount'].replace(',','.')), 'kerroin': float(yhd.string.replace(',', '.')), 'omakerr':0.0}

heppoja = []
heppoja = Check.Hepoja(koodi)   
  
for l1 in range(1,heppoja[l-1][1]+1):
    for l2 in range(1,heppoja[l][1]+1):
        for l3 in range(1,heppoja[l+1][1]+1):
            for l4 in range(1,heppoja[l+2][1]+1):
                yhd = [l1,l2,l3,l4]
                pyhd = p1[l1-1] * p2[l2-1]* p3[l3-1] * p4[l4-1]
                y = "-".join([str(x) for x in yhd])
                if yhdistelma.ok(yhd,systeemi) and pyhd > 0.000001:
                    omakerr = 1 / pyhd
                    if y in rivit.keys():
                        if omakerr > rivit[y]['kerroin']:
                            rivit.pop(y)                # poistetaan ylipelatut kelvolliset rivit
                        else:
                            rivit[y]['omakerr'] = omakerr
                    elif omakerr < 5 * jako:            # pelaamattomat rivit
                        rivit[y] = { 'pelattu': 0.0, 'kerroin' : 5 * jako, 'omakerr' : omakerr}
                elif y in rivit.keys():
                    rivit.pop(y)                        # poistetaan kelpaamattomat rivit

out = open('/home/kari/Python/Pelit/T4.peli', 'w')
for yhd in rivit:
    kerroin = rivit[yhd]['kerroin']
    omakerr = rivit[yhd]['omakerr']
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
        txt = lyhenne + ';' + pvm + ';' + lahto + ';' + peli + ';' + yhd.replace('-', '/') + ';'
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
print 'Vaihto: ' + '{0:.0f}'.format(vaihto) + ' / Jako: '+ '{0:.0f}'.format(jako)
print 'Min: ' + '{0:.1f}'.format(minlunde) + ' / Average: ' + '{0:.1f}'.format(avelunde / omatn) + ' / Max: ' + '{0:.1f}'.format(maxlunde)
print '<<<<<>>>>>'
out.flush()
out.close()
#analyysi.Analyysi('/home/kari/Python/Pelit/T4.peli')

