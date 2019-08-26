'''Programa que integra diversos protótipos.'''

import copy
import random
import estruturas as est
import numpy as np
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import tenney as tn
from incerto_principium.classe_incerto import IncertoPrincipium
from makenote import Protocolo_MIDI2
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, ward, fcluster, fclusterdata
from scipy.cluster.vq import kmeans2, whiten
from scipy.optimize import differential_evolution
from scipy.ndimage.measurements import center_of_mass
from evolucao import fitness
from grafico_pb import imprime_plot


TENSOES = [0, 7, 5, 4, 9, 3, 8, 2, 10, 1, 11, 6]
PESOS = [22.5, 3, 1, 20]
MIDI2PHON = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
             0.0, 0.0, 0.0, 0.0, 0.013, 0.036, 0.062, 0.087, 0.113, 0.138,
             0.164, 0.19, 0.215, 0.24, 0.265, 0.29, 0.313, 0.336, 0.358,
             0.38, 0.4, 0.42, 0.438, 0.456, 0.474, 0.492, 0.51, 0.528,
             0.545, 0.562, 0.578, 0.595, 0.612, 0.627, 0.642, 0.657,
             0.672, 0.687, 0.702, 0.716, 0.731, 0.745, 0.759, 0.771,
             0.785, 0.797, 0.81, 0.823, 0.835, 0.847, 0.859, 0.871, 0.883,
             0.895, 0.906, 0.916, 0.927, 0.937, 0.946, 0.955, 0.964,
             0.971, 0.979, 0.985, 0.99, 0.995, 0.998, 0.999, 1.0, 0.999,
             0.996, 0.991, 0.986, 0.979, 0.97, 0.961, 0.953, 0.945, 0.941,
             0.942, 0.947, 0.957, 0.971, 0.987, 1.003, 1.02, 1.035, 1.05,
             1.063, 1.074, 1.082, 1.085, 1.082, 1.072, 1.053, 1.029,
             1.004, 0.98, 0.956, 0.933, 0.912, 0.892, 0.872, 0.855, 0.839,
             0.823, 0.809, 0.795, 0.78, 0.766, 0.753, 0.744, 0.738, 0.74,
             0.753]


class Partitura():
        def __init__(self, nome_arquivo, listas, tempo_final):
            self.listas = listas
            self.duracao_total = tempo_final
            self.incerto = IncertoPrincipium()
            self.nome_arquivo = nome_arquivo
            self.lista_de_notas = self.ativa()

        def ativa(self):
            saida = []
            tempo_total = 0
            try:
                while tempo_total < self.duracao_total:
                    informacoes = [float(i[int(tempo_total * 5)])
                                   for i in self.listas]

                    nota = self.incerto.proxima_nota(informacoes[2])
                    nota[0] += np.round(informacoes[3])
                    nota[1] *= informacoes[0] + np.random.randint(24) - 12
                    nota[2] *= informacoes[1]

                    saida.append([tempo_total,
                                  int(nota[0]),
                                  int(round(nota[1])),
                                  nota[2]])

                    tempo_total += nota[2]
            except IndexError:
                print('fim com erro de indice. (thread IncertoOffline)')
            return saida


def gera_seed():
    return np.random.randint(0, 4294967295, dtype='uint32')


if __name__ == '__main__':

    # Inicia Seeds automaticamente
    SEED_PERFIS = gera_seed()
    SEED_INCERTO = gera_seed()

    # Atualiza seed de perfis
    np.random.seed(SEED_PERFIS)

    # Cria instancia de peca
    peca = est.Peca([47, 90], [10, 115])
    perfis_prontos = peca.contornos_normalizados

    # Imprime dados da peca
    print('seed perfis:', SEED_PERFIS, 'seed incerteza:', SEED_INCERTO)
    print('duracao total:', peca.duracao)
    print('quantidade de seções:', len(peca.contidos), '\n')

    # Atualiza seed
    np.random.seed(SEED_INCERTO)

    partitura = Partitura('_'.join([str(SEED_PERFIS),
                                    str(SEED_INCERTO)]),
                          perfis_prontos, peca.duracao)

    # SEPARA NOTAS E PAUSAS
    lista_notas, lista_pausas = [], []
    for nota in partitura.lista_de_notas:
        if nota[2] == 0:
            lista_pausas.append(nota)
        else:
            lista_notas.append(nota)

    # ____________________________________________________________________
    # INTENSIDADE

    gestos = [np.log1p(nota[3] / lista_notas[i - 1][3]) * MIDI2PHON[nota[1]]
              for i, nota in enumerate(lista_notas)]
    # gestos = []
    # for i in range(1, len(lista_notas)):
    #     aceleracao = np.log1p(lista_notas[i][3] /
    #                           lista_notas[i - 1][3]) * 100
    #     intervalo = abs(lista_notas[i - 1][1] -
    #                     lista_notas[i][1]) % 12
    #     tensao = 12 - TENSOES.index(intervalo)

    #     # EQUACAO PARA GESTUAL
    #     gestos.append((2 * aceleracao) + tensao)

    gestos = list(np.interp(gestos, (min(gestos), max(gestos)), (0, 127)))
    gestos.insert(0, lista_notas[0][2])
    andamentos = [partitura.listas[1][int(nota[0] * 5)]
                  for nota in lista_notas]
    andamentos = np.interp(andamentos,
                           (min(andamentos), max(andamentos)),
                           (0, 1))
    for i, nota in enumerate(lista_notas):
        if nota[2] < 0:
            nota[2] = 0
        elif nota[2] > 127:
            nota[2] = 127
        peso1 = (andamentos[i] * 0.25)
        peso2 = 1 - peso1
        # Equacao para reunir diferentes fatores da intensidade
        x = ((nota[2] * peso1) + (gestos[i] * peso2)) * 0.7
        nota[2] = int(x + (127 * 0.3))
    # # ____________________________________________________________________

    # SEPARA OS CLANGS
    lista_clangs = tn.separa_clangs(lista_notas, PESOS)
    lista_secoes, secoes_plana = tn.separa_secoes(lista_clangs,
                                                  PESOS)

    centros_secs = []
    for secao in secoes_plana:
        ponto = [0, 0, 0, 0]
        for nota in secao:
            for i in range(len(nota)):
                ponto[i] += nota[i]
        for i in range(len(nota)):
            ponto[i] /= len(secao)
        centros_secs.append(ponto)

    ''' ‘braycurtis’, ‘canberra’, ‘chebyshev’, ‘cityblock’, ‘correlation’,
    ‘cosine’, ‘dice’, ‘euclidean’, ‘hamming’, ‘jaccard’, ‘jensenshannon’,
    ‘kulsinski’, ‘mahalanobis’, ‘matching’, ‘minkowski’, ‘rogerstanimoto’,
    ‘russellrao’, ‘seuclidean’, ‘sokalmichener’, ‘sokalsneath’, ‘sqeuclidean’,
    ‘yule’.'''

    # 'seuclidean' eh bom para criar diferencas em ataque, ‘mahalanobis’ tbm
    # 'jaccard'
    cores = ['red', 'green', 'blue', 'orange', 'purple']
    # X = ward(pdist(centros_secs, metric='euclidean'))
    # etiquetas = list(fcluster(X, 10,
    #                           criterion='distance'))
    centroide_, labels = kmeans2(centros_secs, len(peca.contidos),
                                 iter=30, minit='points')
    print(labels)

    # # # Separa notas nas secoes grandes
    container_grande = []
    for i in range(len(peca.contidos)):
        container_grande.append([])

    # # LISTA de notas = lista de clangs / lista de clangs = lista de secoes
    j = 0
    for i, e in enumerate(labels):
        print(e)
        for nota in secoes_plana[i]:
            container_grande[e].append(lista_notas[j])
            j += 1

    # # # AFASTA SECOES NO TEMPO
    container_grande.sort(key=lambda x: x[0][0])

    somatoria = 0
    for i in range(1, len(container_grande)):
        dur_media = abs(container_grande[i - 1][-1][0] -
                        container_grande[i][0][0])

        media_intens = (sum([nota[2] for nota in container_grande[i - 1]]) /
                        len(container_grande[i - 1]))
        media_dur = (sum([nota[3] for nota in container_grande[i - 1]]) /
                     len(container_grande[i - 1]))
        # print((((media_intens / media_dur) * 0.01) + 1), dur_media)

        # dur_media *= (((media_intens / media_dur) * 0.05) + 1)
        for nota in container_grande[i]:
            nota[0] += somatoria + (media_dur * 0.25)
        somatoria += dur_media

    for i in range(1, len(container_grande)):
        indice = partitura.lista_de_notas.index(container_grande[i - 1][-1])
        inicio = (container_grande[i - 1][-1][0] +
                  container_grande[i - 1][-1][3])
        duracao_nova = abs(inicio - container_grande[i][0][0])
        partitura.lista_de_notas.insert(indice + 1,
                                        [inicio, 0, 0, duracao_nova])

    # APLICA SPREAD
    num_spread = np.random.random_integers(1, len(peca.contidos) / 2)
    for i in range(num_spread):
        indices_spread = np.random.choice(range(1, len(peca.contidos)),
                                          num_spread, replace=False)
    print(indices_spread, num_spread)
    for indx in indices_spread:
        sec_spread = tn.separa_clangs(container_grande[indx], PESOS)
        # print(sec_spread, '\n')
        pontas = []
        for clang in [sec_spread[0], sec_spread[-1]]:
            coluna = [nota[1] for nota in clang]
            pontas.append(np.mean(coluna))
        gap = abs(pontas[0] - pontas[1])
        lista_spread = np.linspace((pontas[0] - min(pontas)) / gap,
                                   (pontas[1] - min(pontas)) / gap,
                                   num=len(sec_spread))

        for clang in sec_spread:
            j = 0
            centro_de_massa, fronteiras = [], []
            for i in range(len(clang[0])):
                coluna = [nota[i] for nota in clang]
                centro_de_massa.append(np.mean(coluna))
                fronteiras.append((min(coluna), max(coluna)))
            coluna2 = []
            for i, nota in enumerate(clang):
                # print(fronteiras[1][0])
                nota[1] = (nota[1] - fronteiras[1][0]) * lista_spread[j]
                coluna2.append(nota[1])
                j += 1
            media_2 = np.mean(coluna2)
            for nota in clang:
                nota[1] = int(nota[1] + centro_de_massa[1] - media_2)

    # CRIA ARRAY PARA FUNCAO FITNESS
    bordas = []
    for i in range(1, len(container_grande)):
        bordas.append((int((90 - max([nota[1]
                                      for nota in container_grande[i]]))),
                       int((47 - min([nota[1]
                                      for nota in container_grande[i]])))))
        bordas.append((int((127 - max([nota[2]
                                       for nota in container_grande[i]]))),
                       int((10 - min([nota[2]
                                      for nota in container_grande[i]])))))

    # APLICA DIFFERENTIAL EVOLUTION
    resultado = differential_evolution(fitness, bordas,
                                       args=container_grande,
                                       maxiter=20, popsize=20)
    mudanca = [np.round(x) for x in resultado.x]
    for i, secao in enumerate(container_grande[1:]):
        for nota in secao:
            nota[1] += mudanca[i * 2]
            nota[2] += mudanca[(i * 2) + 1]

    for clang in lista_clangs:
        aumento = np.round((127 - clang[0][2]) * 0.1)
        outras_notas = len(clang[1:])
        reducao = aumento / outras_notas
        clang[0][2] += aumento
        for nota in clang[1:]:
            nota[2] -= reducao

    for sec in secoes_plana:
        aumento = np.round((127 - sec[0][2]) * 0.1)
        outras_notas = len(sec[1:])
        reducao = aumento / outras_notas
        sec[0][2] += aumento
        for nota in sec[1:]:
            nota[2] -= reducao

    # imprime_plot(lista_notas,
    #              peca.contornos_basicos,
    #              ''.join(['./figuras/', str(SEED_INCERTO),
    #                       '_', str(SEED_PERFIS), '.png']))

    # imprime_plot(lista_notas,
    #              lista_clangs,
    #              secoes_plana,
    #              ''.join(['./figuras/', str(SEED_INCERTO),
    #                       '_', str(SEED_PERFIS), '.png']))

    # GRAFICOS ___________________________________________________________
    # fig = plt.figure(figsize=(5, 2), dpi=300)
    # duracoes = [peca.contidos[i].duracao for i in range(len(peca.contidos))]
    # eixo_x_secoes = [sum(duracoes[:i]) for i in range(len(duracoes) + 1)]

    # eixo_1 = fig.add_subplot(311,
    #                          autoscaley_on=True,
    #                          facecolor='black',
    #                          yticks=[60],
    #                          yticklabels='Dó',
    #                          xticks=eixo_x_secoes)

    # eixo_1.grid(True, 'both', 'x', linewidth=0.2, color='white')
    # eixo_x_secoes = ['{:d}:{:02d}'.format(int(i // 60), int(i % 60))
    #                  for i in eixo_x_secoes]
    # eixo_1.xaxis.set_ticklabels(eixo_x_secoes)
    # eixo_1.yaxis.get_ticklabels()[0].set_fontsize(4)
    # for label in eixo_1.xaxis.get_ticklabels():
    #     label.set_rotation(45)
    #     label.set_fontsize(4)

    # # Desenha retangulos
    # objeto_norm = colors.Normalize(0, 127, True)
    # mapa_cor = cmx.ScalarMappable(objeto_norm, plt.cm.plasma)
    # colecao_retangulos = []
    # for nota in partitura.lista_de_notas:
    #     if nota[2] != 0:
    #         eixo_1.add_patch(Rectangle((nota[0], nota[1]),
    #                                    nota[3],
    #                                    1,
    #                                    facecolor=mapa_cor.to_rgba(nota[2])))

    # # Desenha linha do Do central
    # eixo_1.plot((0, partitura.lista_de_notas[-1][0] +
    #              partitura.lista_de_notas[-1][3]),
    #             (60, 60), color='r', linewidth=0.2)

    # eixo_2 = fig.add_subplot(312,
    #                          autoscaley_on=True,
    #                          facecolor='black')
    # for i, secao in enumerate(container_grande):
    #     for nota in secao:
    #         eixo_2.scatter(nota[0] / PESOS[0],
    #                        nota[1] / PESOS[1],
    #                        c=cores[i], s=2, marker='s')

    # eixo_3 = fig.add_subplot(313,
    #                          autoscaley_on=True)
    # # objeto_norm = colors.Normalize(0, len(secoes_plana), True)
    # # mapa_cor = cmx.ScalarMappable(objeto_norm, plt.cm.Accent)
    # for i, secao in enumerate(secoes_plana):
    #     for nota in secao:
    #         if i % 2:
    #             cor = 'blue'
    #         else:
    #             cor = 'red'
    #         eixo_3.scatter(nota[0] / PESOS[0],
    #                        nota[1] / PESOS[1],
    #                        c=cor, s=1, marker='s')

    # eixo_1.autoscale()
    # eixo_2.autoscale()
    # eixo_3.autoscale()
    # plt.plot(range(len(MIDI2PHON)), MIDI2PHON, c='black')
    # plt.show()

    # TOCADOR ____________________________________________________________
    tocador = Protocolo_MIDI2()
    tocador.iniciar()
    for i in range(len(partitura.lista_de_notas)):
        tocador.makenote(int(partitura.lista_de_notas[i][1]),
                         int(partitura.lista_de_notas[i][2]),
                         partitura.lista_de_notas[i][3], 0)
        sleep(partitura.lista_de_notas[i][3])
    sleep(1)
    tocador.finalizar()
