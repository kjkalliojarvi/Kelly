__author__ = 'kari'

import datetime


def pros(koodi):
    pvm = datetime.datetime.now().strftime('%d%m%Y')
    p = [[] for l in xrange(13)]
    rr = '/home/kari/Python/Prosentit/' + koodi + '_' + pvm +'.txt'
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
                p[i-1].append(int(a)/100.0)

    return p
