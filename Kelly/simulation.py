from . import get_data

import os
from collections import Counter
import numpy as np
import pandas as pd

PELIT_FOLDER = os.environ['PELIT_FOLDER']


def t_peli_simu(args, peliprosentit):
    t_peli = get_data.get_json(PELIT_FOLDER + args.pelimuoto[:2] + '.json')
    simulation = get_data.get_json(PELIT_FOLDER + 'simulation.json')
    pelipros = {}
    for key in peliprosentit.keys():
        p_sum = sum(peliprosentit[key])
        pelipros[key] = [p/p_sum for p in peliprosentit[key]]
    results, systeemi = run_simulation(t_peli, simulation, pelipros)
    df = pd.DataFrame.from_records(results, columns=['hajotus', 'kerroin'])
    pd.set_option('display.max_rows', None)
    tulos = pd.DataFrame()
    gb = df.value_counts('hajotus', normalize=True)
    tulos['hajotus'] = gb.index
    tulos['todennäköisyys'] = gb.values
    rivimaara = []
    minimi = []
    maksimi = []
    keskiarvo = []
    for hajotus in gb.index:
        rivit = get_data.rivit_abcd(hajotus, systeemi)
        mini = round(min(df[df.hajotus == hajotus]['kerroin']), 1)
        ka = round(pd.DataFrame.mean(df[df.hajotus == hajotus]['kerroin']), 1)
        maxi = round(max(df[df.hajotus == hajotus]['kerroin']), 1)
        rivimaara.append(len(rivit))
        minimi.append(mini)
        maksimi.append(maxi)
        keskiarvo.append(ka)
    tulos['rivimaara'] = rivimaara
    tulos['minimi'] = minimi
    tulos['keskiarvo'] = keskiarvo
    tulos['maksimi'] = maksimi
    print(tulos)
    vali = '-' * 80
    print(vali)
    jakauma = abcd_jakauma(tulos)


def run_simulation(t_peli, simulation, pelipros):
    results = [('', 1)] * simulation['samples']
    systeemi = {}
    for i in range(t_peli['lahtoja']):
        lahto = 'L' + str(i + 1)
        prosentit = pelipros[str(i + 1)]
        abcd = get_data.split_abcd(prosentit, simulation['rajat'])
        samples = np.random.choice(np.arange(1, len(prosentit) + 1),
                                   simulation['samples'], p=prosentit)
        sampleresults = []
        apu = []
        for sample in samples:
            category = get_data.get_category(abcd, sample)
            pros = prosentit[sample - 1]
            sampleresults.append((category, pros))
        for q in zip(results, sampleresults):
            apu.append((q[0][0]+q[1][0], q[0][1]*q[1][1]))
        results = apu
        systeemi[lahto] = abcd
    apu = []
    for result in results:
        apu.append((''.join(sorted(result[0])), 0.65 * t_peli['panos'] / result[1]))
    return apu, systeemi


def abcd_jakauma(tulos):
    jakauma = {'A': {}, 'B': {}, 'C': {}, 'D': {}, 'X': {}}
    for _, row in tulos.iterrows():
        lahtoja = len(row['hajotus'])
        abcd = Counter(row['hajotus'])
        prob = row['todennäköisyys']
        lkmA = abcd.get('A', 0)
        jakauma['A'][str(lkmA)] = jakauma['A'].get(str(lkmA), 0) + prob
        lkmB = abcd.get('B', 0)
        jakauma['B'][str(lkmB)] = jakauma['B'].get(str(lkmB), 0) + prob
        lkmC = abcd.get('C', 0)
        jakauma['C'][str(lkmC)] = jakauma['C'].get(str(lkmC), 0) + prob
        lkmD = abcd.get('D', 0)
        jakauma['D'][str(lkmD)] = jakauma['D'].get(str(lkmD), 0) + prob
        lkmX = abcd.get('X', 0)
        jakauma['X'][str(lkmX)] = jakauma['X'].get(str(lkmX), 0) + prob
    df = pd.DataFrame(jakauma)
    df_transposed = df.T
    cols = sorted(df_transposed.columns.tolist())
    print(df_transposed[cols])
    return jakauma