import os


PELIT_FOLDER = os.environ['PELIT_FOLDER']


def analysoi(args):
    with open(PELIT_FOLDER + args.pelimuoto_ + '.peli', 'r') as pelifile:
        pelit = {'duo': 2, 'troikka': 3, 't4': 4, 't5': 5, 't6': 6, 't7': 7, 't8': 8}
        lahtoja = pelit[args.pelimuoto_]
        laskuri = {str(i): {str(i): 0 for i in range(1, 17)} for i in range(1, lahtoja + 1)}
        kokpanos = {str(i): {str(i): 0 for i in range(1, 17)} for i in range(1, lahtoja + 1)}
        while True:
            raaka = pelifile.readline().split(';')
            if raaka[0] == 'Yht':
                riveja = raaka[1]
                total = raaka[2]
                break
            rivi = raaka[4].split('/')
            panos = float(raaka[5])
            for lahto, numero in enumerate(rivi, 1):
                laskuri[str(lahto)][numero] += 1
                kokpanos[str(lahto)][numero] += panos

    def tulosta(title, getter, rivisumma=False):
        print(f'\n{title}')
        header = f'  {"lä":>4} │' + ''.join(f'{h:>4}' for h in range(1, 17))
        print(header)
        print('  ' + '─' * (len(header) - 2))
        for ll in range(1, lahtoja + 1):
            solut = ''.join(f'{getter(ll, h):>4.0f}' for h in range(1, 17))
            rivi = f'  {ll:>4} │{solut}'
            if rivisumma:
                summa = sum(getter(ll, h) for h in range(1, 17))
                rivi += f'  = {summa:.0f}'
            print(rivi)

    print(f'\n{args.pelimuoto_.upper()}  —  rastit yhteensä: {riveja}')
    tulosta('Rastit lähdöittäin',
            lambda ll, h: laskuri[str(ll)][str(h)], rivisumma=True)
    tulosta('%-osuudet riveistä',
            lambda ll, h:
                100 * float(laskuri[str(ll)][str(h)]) / float(riveja))
    tulosta('%-osuudet rahasta',
            lambda ll, h:
                100 * float(kokpanos[str(ll)][str(h)]) / float(total))
