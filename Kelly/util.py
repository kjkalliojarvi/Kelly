import os


PELIT_FOLDER = os.environ['PELIT_FOLDER']

RULE = '─' * 46


def otsikko(title):
    """Print a titled section header to the console."""
    print(f'\n{title}')
    print(RULE)


def write_to_file(bets, peli, args, metadata, huomio=''):
    omatn = 0
    tot_panos = 0
    lunastus = []
    filename = f'{PELIT_FOLDER}{peli}.peli'
    otsikko(f'{peli.upper()}  {metadata.lyhenne} {metadata.pvm}  '
            f'lähtö {args.lahto}{huomio}')
    if bets:
        print(f'  {"yhdistelmä":<20}{"panos":>8}{"kerroin":>10}')
        print(f'  {"-" * 44}')
    with open(filename, 'w') as pelifile:
        for bet in bets:
            omatn += (1 / bet.oma_kerroin)
            tot_panos += bet.pelipanos
            lunastus.append(bet.pelipanos * bet.kerroin)
            txt = (
                f'{metadata.lyhenne};{metadata.pvm};{args.lahto};'
                f'{peli.upper()};{bet.yhdistelma};'
                f'{bet.pelipanos};{bet.pelipanos}'
            )
            print(f'  {bet.yhdistelma:<20}{bet.pelipanos:>8}'
                  f'{bet.kerroin:>10.0f}')
            pelifile.write(txt + '\n')
        print(f'  {"-" * 44}')
        print(f'  {"Rivejä yht.":<20}{len(bets):>8}{tot_panos:>10.1f} €')
        pelifile.write(f'Yht;{len(bets)};{tot_panos:.1f}')
    if len(lunastus) > 0:
        avelunde = sum(lunastus)/len(lunastus)
        footer(omatn, tot_panos, metadata,
               min(lunastus), avelunde, max(lunastus))


def footer(omatn, total, metadata, minlunde, avelunde, maxlunde):
    tomatn = 0.0
    if omatn > 0.0001:
        tomatn = total / omatn
    print(RULE)
    print(f'  {"Oma todennäköisyys":<22}: {100 * omatn:.1f} %  '
          f'(kerroin {tomatn:.2f})')
    print(f'  {"Vaihto / Jako":<22}: {metadata.vaihto} / {metadata.jako}')
    try:
        print(f'  {"Lunastus min/ka/max":<22}: {minlunde:.1f} / '
              f'{avelunde:.1f} / {maxlunde:.1f}')
    except (ZeroDivisionError, TypeError):
        pass
    print(RULE)
