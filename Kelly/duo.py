import sys
import json
import data

systeemi = []
koodi = sys.argv[1]
lahto = sys.argv[2]
print('Duo: Ravit ' + koodi + ', Lähtö ' + lahto)

prosentit = data.prosentit(koodi)
p1 = [p/100 for p in prosentit[lahto]]
p2 = [p/100 for p in prosentit[str(int(lahto) + 1)]]

duo_paraf = open('duo_para.json')
duo_para = json.dumps(duo_paraf.read())  # minKelly, panos, minLunastus
duof = open('duo.json')
duo = json.dumps(duof.read())  # oikein, L1, L2

kerroinxml = data.kertoimet(koodi, lahto, 'duo')

kerroindata = kerroinxml.find('pool')
vaihto = kerroindata['net-sales']
jako = kerroindata['net-pool']
lyhenne = kerroinxml.card['code']
pvm = kerroinxml.card['date'][0:5]
peli = kerroindata['type']

omatn = 0.0
lkm = 0
total = 0.0
minlunde = 100000.0
maxlunde = 0.0
avelunde = 0.0

out = open('/home/kari/Python/Pelit/duo_peli.csv', 'w')
for yhd in kerroinxml.find_all('probable'):
    y = [int(y) for y in yhd['combination'].split('-')]

    if data.yhdistelma_ok(y, duo):
        kerroin = float(yhd.string.replace(',', '.'))
        if int(kerroin) == 0:
            # max kerroin jos yhdistelmää ei pelattu
            kerroin = float(jako.replace(',', '.'))
        omakerr = 10000.0
        if (p1[y[0] - 1] * p2[y[1] - 1]) > 0.00001:
            omakerr = 1 / (p1[y[0] - 1] * p2[y[1] - 1])

        if kerroin > omakerr > 0:
            kelly = (kerroin - omakerr) / (kerroin - 1) / omakerr
            kert = int(kelly / duo_para['minKelly'])
            lunde = kert * duo_para['panos'] * kerroin
            if lunde > duo_para['minLunastus']:
                lkm += 1
                omatn += 1 / omakerr
                total += kert * duo_para['panos']
                avelunde += lunde / omakerr
                if lunde < minlunde:
                    minlunde = lunde
                if lunde > maxlunde:
                    maxlunde = lunde
                txt1 = lyhenne + ';' + pvm + ';' + lahto + ';' + peli + ';'
                txt2 = yhd['combination'].replace('-', '/') + ';'
                ps = '{0:.1f}'.format(kert * duo_para['panos'])
                print(txt1 + txt2 + ps + ';' + ps)
                out.write(txt1 + txt2 + ps + ';' + ps + '\n')


print('Yht;' + str(lkm) + ';' + '{0:.1f}'.format(total))
out.write('Yht;' + str(lkm) + ';' + '{0:.1f}'.format(total))
print('<<<<<>>>>>')
tomatn = 0.0
if omatn > 0.0001:
    tomatn = total / omatn
print('Oma todennäköisyys: ' + '{0:.1f}'.format(100*omatn) + ' % // ' +
      '{0:.1f}'.format(tomatn))
print('Vaihto: ' + vaihto + ' / Jako: ' + jako)
print('Min: ' + '{0:.1f}'.format(minlunde) + ' / Average: ' +
      '{0:.1f}'.format(avelunde/omatn) +
      ' / Max: ' + '{0:.1f}'.format(maxlunde))
print('<<<<<>>>>>')
out.flush()
out.close()
