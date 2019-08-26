'''Biblioteca para funcoes de Temporal Gestalt'''
import numpy as np
from pathlib import Path
from scipy.spatial.distance import pdist
import csv


PESOS = [1, 1, 10]


def abre_arquivo():
    '''Funcao para abrir um arquivo da biblioteca de outputs, aleatoriamente.'''
    diretorio = Path('./outputs_salvos')
    arquivo = np.random.choice([x for x in diretorio.iterdir() if x.is_dir()])
    arquivo = ''.join(['./', str(arquivo), '/', arquivo.name, '.csv'])

    lista_notas, lista_pausas = [], []
    with open(arquivo, 'r') as aberto:
        arq_completo = csv.reader(aberto)
        for linha in arq_completo:
            if float(linha[2]) != 0:
                lista_notas.append(list(map(float, linha)))
            else:
                lista_pausas.append(list(map(float, linha)))

    return lista_notas, lista_pausas


def reinsere_pausas(lista_notas, lista_pausas):

    lista_pausas.reverse()
    # print(len(lista_pausas))
    for i, clang in enumerate(lista_notas):
        # print(len(clang))
        for j in range(1, len(clang)):
            # print(clang[j - 1][0], lista_pausas[-1][0], clang[j][0])

            if clang[j - 1][0] < lista_pausas[-1][0] and \
               clang[j][0] > lista_pausas[-1][0]:

                # print('\n')
                clang.insert(j, lista_pausas.pop())

        try:
            if lista_notas[i][-1][0] < lista_pausas[-1][0] and \
               lista_notas[i + 1][0][0] > lista_pausas[-1][0]:
                lista_notas[i].append(lista_pausas.pop())

        except IndexError:
            print('ai, deu erro')

        # print(clang, '\n')
        # print(len(clang))
    # print(len(lista_pausas))


def separa_clangs(lista, pesos, n_param=3):
    # Particao de temporal gestalt
    distancias = []
    for i in range(1, len(lista)):
        # Calcula duracao entre uma nota (seu onset) e a proxima
        dist = [((abs(lista[i - 1][parametro] -
                      lista[i][parametro]) * pesos[parametro])**2)
                for parametro in range(n_param)]
        distancias.append(np.sqrt(sum(dist)))

    lista_tgs, tg = [], [lista[0]]
    for i in range(1, len(distancias) - 1):
        tg.append(lista[i])
        if (distancias[i] > distancias[i - 1]) and \
           (distancias[i] > distancias[i + 1]):
            lista_tgs.append(tg.copy())
            tg.clear()
    lista_tgs[-1].append(lista[-1])
    return lista_tgs


def separa_secoes(lista_de_clangs, pesos):
    pontos = []
    for clang in lista_de_clangs:
        lista_parametros = [0 for parametro in range(len(pesos))]
        tamanho = 0
        for nota in clang:
            for i in range(len(pesos)):
                lista_parametros[i] += nota[i]
            tamanho += 1
        for item in lista_parametros:
            item /= tamanho
        pontos.append([i / tamanho for i in lista_parametros])
        del lista_parametros
    lista_secoes = separa_clangs(pontos, pesos, n_param=4)

    secoes, j = [], 0
    for i, secao in enumerate(lista_secoes):
        secoes.append([])
        for clang in secao:
            secoes[i].append(lista_de_clangs[j])
            j += 1

    return secoes, achata_secao(secoes)


def achata_secao(lista):
    saida = []
    for secao in lista:
        container = []
        for clang in secao:
            for nota in clang:
                container.append(nota)
        saida.append(container)
    return saida

    # return separa_clangs(pontos, pesos)
    # pontos_medios, distancias = [], []
    # for clang in lista_de_clangs:
    #     componente_a = 0
    #     componente_i = 0
    #     componente_d = 0
    #     for notas in clang:
    #         componente_a += notas[1] * pesos[1]
    #         componente_i += notas[2] * pesos[2]
    #         componente_d += notas[0] * pesos[0]
    #     componente_a /= len(clang)
    #     componente_i /= len(clang)
    #     componente_d /= len(clang)
    #     pontos_medios.append([componente_a, componente_i, componente_d])

    # for i in range(1, len(pontos_medios)):
    #     distancias.append(abs(sum(pontos_medios[i]) -
    #                           sum(pontos_medios[i - 1])))

    # lista_tgs, tg = [], [lista_de_clangs[0]]
    # for i in range(1, len(distancias) - 1):
    #     tg.append(lista_de_clangs[i])
    #     if (distancias[i] > distancias[i - 1]) and \
    #        (distancias[i] > distancias[i + 1]):
    #         # print(tg)
    #         lista_tgs.append(tg.copy())
    #         tg.clear()

    # lista_tgs[-1].append(lista_de_clangs[-1])

    # return lista_tgs


if __name__ == '__main__':

    lista_notas, lista_pausas = abre_arquivo()

    sacola = temporal_gestalt(lista_notas, PESOS)
    secoes = tg_segunda_ordem(sacola, PESOS)
    for clang in secoes:
        for nota in clang:
            for elem in nota:
                print(elem)
        print('\n')
