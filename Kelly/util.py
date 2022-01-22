from decouple import config


PELIT_FOLDER = config('PELIT_FOLDER')


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
