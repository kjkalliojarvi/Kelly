from decouple import config
from itertools import product

from Kelly.kelly_calc import write_to_file

from . import get_data

PELIT_FOLDER = config('PELIT_FOLDER')


def voittaja(args, prosentit, metadata, kertoimet):
    p1 = [p/100 for p in prosentit[args.lahto]]
    print(f'Voittaja: Lähtö {args.lahto}, vaihto {metadata.vaihto}')
    for voittaja in kertoimet:
        num = int(voittaja['runner'])
        vkerr = float(voittaja.string.replace(',', '.'))
        omavk = 1000
        if p1[num-1] > 0:
            omavk = 1 / p1[num-1]
        if vkerr > omavk:
            kelly = get_data.kelly(vkerr, omavk)
            if kelly > 0.05:
                print(f'{num:2}: {vkerr:3.1f} / {omavk:3.1f} / {100*kelly:3.1f} %')
    print('----- * -----')


def sija(args, prosentit, metadata, kertoimet):
    p1 = [p/100 for p in prosentit[args.lahto]]
    p2 = get_data.p_2(prosentit[args.lahto])
    p3 = get_data.p_3(prosentit[args.lahto])
    print(f'Sija: Lähtö {args.lahto}, vaihto {metadata.vaihto}')
    for sija in kertoimet:
        num = int(sija['runner'])
        yla = float(sija['high-probable'].replace(',', '.'))
        haar = sija['low-probable'] + ' - ' + sija['high-probable']
        sijap = p1[num-1] + p2[num-1] + p3[num-1]
        if sijap > .2:
            if 1/sijap < yla:
                print(f'{num:2}: {haar} / {1/sijap:2.2f}')
    print('----- * -----')


def kaksari(args, prosentit, metadata, kertoimet):
    p1 = [p/100 for p in prosentit[args.lahto]]
    p2 = get_data.p_2(prosentit[args.lahto])
    print(f'Kaksari: Lähtö {args.lahto}, vaihto {metadata.vaihto}')
    for kaksari in kertoimet:
        y = [int(y) for y in kaksari['combination'].split('-')]
        kkerr = float(kaksari.string.replace(',', '.'))
        omakk = 100000.0
        if (p1[y[0] - 1] * p2[y[1] - 1]) > .000001:
            omakk = 1 / (p1[y[0]-1]*p2[y[1]-1]/(1-p2[y[0]-1]) + p1[y[1]-1]*p2[y[0]-1]/(1-p2[y[1]-1]))
        if kkerr > omakk:
            kelly = get_data.kelly(kkerr, omakk)
            if kelly > 0.01:
                print(f'{kaksari["combination"]:>5}: '
                      f'{kkerr:5.1f} / {omakk:4.1f} / {100*kelly:4.1f} %')
    print('----- * -----')


def duo(args, prosentit, metadata, kertoimet):
    print(f'Duo: Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    conf = get_data.get_json(PELIT_FOLDER + 'duo.json')
    pros = {}
    for i in range(2):
        lahto = str(int(args.lahto) + i)
        pros[str(i + 1)] = [p/100 for p in prosentit[lahto]]
    yhdistelmat = list(product(conf['L1'], conf['L2']))
    bets = []
    for yhd in kertoimet:
        y = tuple([int(y) for y in yhd['combination'].split('-')])
        if y in yhdistelmat:
            kerroin = float(yhd.string.replace(',', '.'))
            if int(kerroin) == 0:
                kerroin = metadata.jako  # max kerroin jos yhdistelmää ei pelattu
            oma_kerroin = 1 / get_data.yhdistelma_tn(y, pros)
            yhdistelma = yhd['combination'].replace('-', '/')
            bet = get_data.bet_size(kerroin, oma_kerroin, yhdistelma, conf)
            if bet:
                bets.append(bet)
    write_to_file(bets, 'duo', args, metadata)


def troikka(args, prosentit, metadata, kertoimet):
    print(f'Troikka: Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    conf = get_data.get_json(PELIT_FOLDER + 'troikka.json')
    p1 = [p/100 for p in prosentit[args.lahto]]
    p2 = get_data.p_2(prosentit[args.lahto])
    p3 = get_data.p_3(prosentit[args.lahto])
    bets = []
    for yhd in kertoimet:
        y = [int(y) for y in yhd['combination'].split('-')]
        if get_data.troikka_yhdistelma_ok(y, config):
            kerroin = float(yhd.string.replace(',', '.'))
            if int(kerroin) == 0:
                kerroin = 2.0 * metadata.jako  # max kerroin jos yhdistelmää ei pelattu
            oma_kerroin = 100000.0
            if (p1[y[0] - 1] * p2[y[1] - 1] * p3[y[2] - 1]) > 0.000001:
                oma_kerroin = ((1 - p2[y[0] - 1])*(1-p3[y[0] - 1]-p3[y[1] - 1])) / (p1[y[0] - 1]*p2[y[1] - 1]*p3[y[2] - 1])
            yhdistelma = yhd['combination'].replace('-', '/')
            bet = get_data.bet_size(kerroin, oma_kerroin, yhdistelma, conf)
            if bet:
                bets.append(bet)
    write_to_file(bets, 'troikka', args, metadata)


def t_peli(args, prosentit, metadata, kertoimet):
    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}')
    conf = get_data.get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(conf['lahtoja'])
    pros = {}
    for i in range(conf['lahtoja']):
        lahto = str(int(args.lahto) + i)
        lahto_t_peli = str(i + 1)
        pros[lahto_t_peli] = [p/100 for p in prosentit[lahto]]
        conf['L' + lahto_t_peli] = get_data.split_abcd(pros[lahto_t_peli], conf['rajat'])
    yhdistelmat = get_data.hajotus_rivit(config)
    vain_ylin = 1
    if args.pelimuoto in ['t65']:
        vain_ylin = 2
    if args.pelimuoto in ['t64', 't75', 't86']:
        vain_ylin = 2.5
    bets = []
    for yhd in kertoimet:
        y= tuple([int(y) for y in yhd['combination'].split('-')])
        if y in yhdistelmat:
            kerroin = vain_ylin * float(yhd.string.replace(',', '.')) / conf['panos']
            if int(kerroin) == 0:
                kerroin = metadata.jako / conf['panos'] # max kerroin jos yhdistelmää ei pelattu
            oma_kerroin = 1 / get_data.yhdistelma_tn(y, pros)
            yhdistelma = yhd['combination'].replace('-', '/')
            bet = get_data.bet_size(kerroin, oma_kerroin, yhdistelma, config)
            if bet:
                bets.append(bet)
    write_to_file(bets, pelimuoto, args, metadata)


def t_peli_pros(args, prosentit, metadata, peliprosentit):
    print(f'{args.pelimuoto.upper()} : Ravit {args.ratakoodi}, Lähtö {args.lahto}: PROSENTIT')
    conf = get_data.get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    pelimuoto = 't' + str(conf['lahtoja'])
    pros = {}
    for i in range(conf['lahtoja']):
        lahto = str(int(args.lahto) + i)
        lahto_t_peli = str(i + 1)
        pros[lahto_t_peli] = [p/100 for p in prosentit[lahto]]
        conf['L' + lahto_t_peli] = get_data.split_abcd(pros[lahto_t_peli], conf['rajat'])
    yhdistelmat = get_data.hajotus_rivit(config)

    pelipros = {}
    for key in peliprosentit.keys():
        pelipros[key] = [p/100 for p in peliprosentit[key]]
    vain_ylin = 1
    bets = []
    for yhd in yhdistelmat:
        # vain ylin voittoluokka
        kerroin = (metadata.jako / metadata.vaihto) / get_data.yhdistelma_tn(yhd, pelipros)
        oma_kerroin = 1 / get_data.yhdistelma_tn(yhd, pros)
        yhdistelma = yhd['combination'].replace('-', '/')
        bet = get_data.bet_size(kerroin, oma_kerroin, yhdistelma, config)
        if bet:
            bets.append(bet)
    write_to_file(bets, pelimuoto, args, metadata)


def write_to_file(bets, peli, args, metadata):
    omatn = 0
    tot_panos = 0
    lunastus = []
    filename = f'{PELIT_FOLDER}{peli}.peli'
    with open(filename, 'w') as pelifile:
        for bet in bets:
            omatn += (1 / bet.oma_kerroin)
            tot_panos += bet.pelipanos
            lunastus.append(bet.pelipanos * bet.kerroin)
            txt = (
                f'{metadata.lyhenne};{metadata.pvm};{args.lahto};'
                f'{metadata.peli};{bet.yhdistelma};'
                f'{bet.pelipanos};{bet.pelipanos}'
            )
            print(f'{txt}  =>  {bet.kerroin:.0f}')
            pelifile.write(txt + '\n')
        print(f'Yht;{len(bets)};{tot_panos:.1f}')
        pelifile.write(f'Yht;{len(bets)};{tot_panos:.1f}')
    print('<<<<<>>>>>')
    if len(lunastus) > 0:
        avelunde = sum(lunastus)/len(lunastus)
        footer(omatn, tot_panos, metadata, min(lunastus), avelunde, max(lunastus))


def footer(omatn, total, metadata, minlunde, avelunde, maxlunde):
    tomatn = 0.0
    if omatn > 0.0001:
        tomatn = total / omatn
    print(f'Oma todennäköisyys: {100 * omatn:.1f} % // {tomatn:.1f}')
    print(f'Vaihto: {metadata.vaihto} / Jako: {metadata.jako}')
    try:
        print(
            f'Min: {minlunde:.1f} / Average: {avelunde:.1f} / '
            f'Max: {maxlunde:.1f}'
            )
    except ZeroDivisionError:
        pass
    print('<<<<<>>>>>')
