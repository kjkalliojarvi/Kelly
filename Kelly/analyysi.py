from decouple import config


PELIT_FOLDER = config('PELIT_FOLDER')


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

    print('Rastit ' + str(riveja))
    for i in range(1, 17):
        print('{0:3d} |'.format(i), end="")
    print('')
    print(80 * '=')
    for ll in range(1, lahtoja + 1):
        for h in range(1, 17):
            print('{0:3.0f} |'.format(laskuri[str(ll)][str(h)]), end="")
        print('')
    print('Rastit ')
    a = 0
    for i in range(1, 17):
        print('{0:3d} |'.format(i), end="")
    print('')
    print(80 * '=')
    for ll in range(1, lahtoja + 1):
        a = 0
        for h in range(1, 17):
            print('{0:3.0f} |'.format(laskuri[str(ll)][str(h)]), end="")
            a += laskuri[str(ll)][str(h)]
        print(int(a))
    print('%-osuudet')
    for i in range(1, 17):
        print('{0:3d} |'.format(i), end="")
    print('')
    print(80 * '=')
    for ll in range(1, lahtoja + 1):
        for h in range(1, 17):
            print('{0:3.0f} |'.format(100*float(laskuri[str(ll)][str(h)])/float(riveja)), end="")
        print('')
    print('%-osuudet rahasta')
    for i in range(1, 17):
        print('{0:3d} |'.format(i), end="")
    print('')
    print(80 * '=')
    for ll in range(1, lahtoja + 1):
        for h in range(1, 17):
            print('{0:3.0f} |'.format(100*float(kokpanos[str(ll)][str(h)])/float(total)), end="")
        print('')
