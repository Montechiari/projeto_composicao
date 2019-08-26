'''Funções para usar com scipy.optimize.differential_evolution'''
import numpy as np
import copy
from scipy.spatial.distance import pdist
# from scipy.optimize import differential_evolution
from scipy.spatial import distance


def centroide_clang(clang):
    length = len(clang)
    x, y, z, w = [], [], [], []
    for nota in clang:
        copia = nota.copy()
        x.append(copia[0])
        y.append(copia[1])
        z.append(copia[2])
        w.append(copia[3])

    return [sum(x) / length, sum(y) / length,
            sum(z) / length, sum(w) / length]


def fitness(transformacoes, *partitura):

    partitura = copy.deepcopy(partitura)
    for t in transformacoes:
        t = np.round(t)

    for i in range(len(partitura) - 1):
        for nota in partitura[i + 1]:
            nota[1] += transformacoes[i * 2]
            nota[2] += transformacoes[(i * 2) + 1]

    centroide_clangs = list(map(centroide_clang, partitura))
    somatoria_dist = sum(pdist(centroide_clangs, metric='euclidean'))

    # somatoria_dist = 0
    # for i in range(1, len(partitura)):
    #     somatoria_dist += distance.euclidean(centroide_clang(partitura[i - 1]),
    #                                          centroide_clang(partitura[i]))
    return np.log((1 / somatoria_dist) +
                  (np.sqrt((1 / somatoria_dist**2) + 1)))


if __name__ == '__main__':
    pass
