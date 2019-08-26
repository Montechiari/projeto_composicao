''' Funcoes utilizadas em Incerto Principium (main.py).
    Versão: 0.6          Ultima atualização: 30/07/2017
    Coisas a fazer: terminar função para intensidades;
    formatar score do Csound; formatar melhor o stream
    de music21.
'''
from collections import namedtuple
# from scipy.interpolate import interp1d
import numpy as np
from music21 import *


# Quantos milissegundos sao uma seminima
UNIDADE_MS = 600
SEMINIMA = 1.0 / UNIDADE_MS
DIMENSAO = 100
STD_DEV = 5

Nota = namedtuple('Nota', 't_inicio duracao intensidade altura')


class Cadeia:
    def __init__(self):
        self.dimen = 0
        self.t_prob = []
        self.conteudo = []


# Referencias para midi2freq
MIDI_A4 = 69
FREQ_A4 = 440


def abre_arquivos(nome_do_arquivo):
    '''Abre arquivos de cadeias de Markov.'''
    with open(nome_do_arquivo, 'r') as arquivo:
        lista = arquivo.readlines()
    return lista


def abre_em_finale(lista):
    '''Transforma lista de tupla de notas em formato music21
        e abre a melodia no Finale (no futuro editar página).'''
    parte = stream.Part()
    tetos = []
    duracoes = []

    for TG in lista:
        dur_comp = sum([notas[1] for notas in TG])
        duracoes.append(dur_comp)
        tetos.append(np.ceil(dur_comp / UNIDADE_MS))

    for i in range(len(lista)):
        compasso = stream.Measure()

        falta = tetos[i] * UNIDADE_MS - duracoes[i]
        ts = meter.TimeSignature('{}/4'.format(int(tetos[i])))
        compasso.timeSignature = ts

        for nota in lista[i]:
            if nota[2] != 0:
                compasso.append(note.Note(midi=nota[3], quarterLength=nota[1]*SEMINIMA))
            else:
                compasso.append(note.Rest(quarterLength=nota[1]*SEMINIMA))
        if falta > 0:
            lista[i].append(note.Rest(quarterLength=falta))

        parte.append(compasso)


    # mostra = parte.measures(0, None)
    parte.show()


def cria_perfil_incerteza(tipo, tempo_atual, tempo_total):
    '''Cria perfil de incertezas.'''
    x = tempo_atual/tempo_total
    xp = [0, 0.70, 1]
    if tipo == 'alturas':
        fp = [0, 1, 0]
    elif tipo == 'ritmos':
        fp = [1, 0, 1]
    return np.interp(x, xp, fp)


def escreve_cadeia(lista):
    '''Preenche instancias de Cadeia.'''
    cadeia = Cadeia()
    tamanho = lista[0].split()
    cadeia.dimen = int(tamanho[0])

    for i in range(cadeia.dimen):
        # Escreve cadeia de probabilidades
        cadeia.t_prob.append(lista[i+1].split())
        cadeia.t_prob[i] = list(map(int, cadeia.t_prob[i]))
        # Escreve conteudo
        cadeia.conteudo.append(lista[i+cadeia.dimen+1].split())
        cadeia.conteudo[i] = list(map(int, cadeia.conteudo[i]))
    return cadeia


def faz_perfil():
    '''Monta array com perfil.'''
    array_primario = [0] * DIMENSAO
    #inicializa inicio e fim
    array_primario[int(DIMENSAO*0.5)] = np.random.randint(0, 99)
    sorteia_recursivo(array_primario, 0, DIMENSAO-1)
    return array_primario



#def gera_intensidades(lista):
'''Recebe lista já separada em temporal gestalts
    e imprime sobre elas um padrão dinâmico.
    Por enquanto sem interpolação.'''
    # tempo_total = lista[-1][-1][0] + lista[-1][-1][1]
    # global DIMENSAO
    # DIMENSAO = tempo_total

    # array_primario = faz_perfil()

    # eixo_x = []
    # eixo_y = []
    # i = 0
    # while i < DIMENSAO :
    # 	eixo_y.append(array_primario[i])
    # 	eixo_x.append(i)
    # 	i += np.random.randint(1, DIMENSAO*0.03)
    # eixo_y.append(array_primario[-1])
    # eixo_x.append(DIMENSAO)

    # interpolado = interp1d(eixo_x, eixo_y, kind='quadratic')
    # novo_x = []
    # for clang in lista:
    # 	for nota in clang:
    # 		novo_x.append(nota[0])
    # novo_y = interpolado(novo_x)
    # i = 0
    # for clang in lista:
    # 	for nota in (clang):
    # 		print(novo_y[i])
    # 		i += 1


def gera_tabela_incerta(cadeia, incerteza=0):
    '''Cria uma tabela de probabilidades modificada. '''
    matriz = []
    for i in range(cadeia.dimen):
        linha = []
        for j in range(cadeia.dimen):
            if cadeia.t_prob[i][j] != 0:
                sorteado = np.random.normal(cadeia.t_prob[i][j], incerteza * 10)
                if sorteado >= 0:
                    linha.append(sorteado)
                else: 
                    linha.append(0)
            else:
                linha.append(0)
        matriz.append(linha)
    matriz = [normaliza_lista(linha) for linha in matriz]
    return matriz


def imprime_score(lista):
    '''Imprime no console score de Csound. PRECISA FORMATAR MELHOR!'''
    for nota in lista:
        print('i 1 %f %f %f %f'%(nota[0],nota[1],nota[2],midi2freq(nota[3])))


def inicia():
    '''Inicia processo de abrir arquivos.'''
    alturas = escreve_cadeia(abre_arquivos('./incerto_principium/alturas.txt'))
    ritmos  = escreve_cadeia(abre_arquivos('./incerto_principium/ritmos.txt'))
    return alturas, ritmos


def interpola_linha(x, linha1, linha2):
    '''Faz interpolacao dos valores de duas listas de probabilidades,
        x deve ser um valor de 0 a 1.
    '''
    xp = [0, 1]
    return [round(np.interp(x, xp, list(fp))) for fp in zip(linha1, linha2)]


def inverte_valor(maximo, valor):
    '''Inverte o valor inserido, i.e. 10->0, 0->10.'''
    return (valor*-1)+maximo 

                                                               
def midi2freq(midi_number):
    '''Converte altura midi para frequencia em Hz.'''
    return FREQ_A4 * 2**((midi_number - MIDI_A4) * (1./12.))


def midi2pch(num):
    '''Converte midi para formato PCH do Csound.'''
    return "%d.%02g" % (3 + (num / 12), num % 12)


def normaliza_lista(lista):
    '''Normaliza lista de probabilidades.'''
    minimo = min(lista)
    lista_saida = [item + (minimo * -1)
                   if item != 0 
                   else item
                   for item in lista]
    somatoria = sum(lista_saida)
    if somatoria == 0:
        raise ZeroDivisionError("Erro em normaliza_lista.")
    else:
        lista_saida = [round((item / somatoria) * 100, 3)
                       for item in lista_saida]
    return lista_saida


def sorteia_indice(linha):
    '''Gerador pseudo-aleatorio de distribuiçao arbitrária.'''
    populacao = []
    for indice, elemento in enumerate(linha):
        if elemento > 0:
            for _ in range(int(elemento)):
                populacao.append(indice)
    return np.random.choice(populacao)


def sorteia_recursivo(vetor, inicio, fim):
    """Popula um array de mid-point displacement."""
    if (fim - inicio) > 1 :
        valor_medio = int((fim + inicio)*0.5)

        vetor[valor_medio] = (np.average([vetor[inicio], vetor[fim]])
                           + np.random.normal(0, STD_DEV))

        while vetor[valor_medio] < 0 or vetor[valor_medio] > 127:
            vetor[valor_medio] = (np.average([vetor[inicio], vetor[fim]]) 
                               + np.random.normal(0, STD_DEV))

        sorteia_recursivo(vetor, inicio, valor_medio)
        sorteia_recursivo(vetor, valor_medio, fim)


def temporal_gestalt(lista, peso_Dur, peso_Alt):
    '''Identifica temporal gestalts de James Tenney (apenas duração e altura).'''
    TG, lista_saida,sem_pausa = [], [], []
    #Calcula distancias do espaço musical sem contar pausas.
    duracao_temp = 0
    for i in range(len(lista)-1, -1, -1):
        if lista[i][2] == 0:
            duracao_temp += lista[i][1]
        else:
            duracao_temp += lista[i][1]
            distancia = duracao_temp*peso_Dur + lista[i][3]*peso_Alt
            tupla_nota = (distancia, lista[i])
            sem_pausa.insert(0, tupla_nota)
            duracao_temp = 0
    #Separa clangs sem pausas.
    TG.append(sem_pausa[0][1])
    for i in range(1, len(sem_pausa) - 1):
        TG.append(sem_pausa[i][1])
        if(sem_pausa[i-1][0] < sem_pausa[i][0] and sem_pausa[i+1][0] < sem_pausa[i][0]):
            lista_saida.append(TG)
            TG = []
    TG.append(sem_pausa[-1][1])
    lista_saida.append(TG)
    #Adiciona as pausas.
    j = 0
    for i in range(1, len(lista_saida)):
        while lista[j][0] < lista_saida[i][0][0]:
            if lista[j][2] == 0:
                lista_saida[i-1].append(lista[j])
            j += 1
        if i == len(lista_saida) - 1:
            while j < len(lista):
                if lista[j][2] == 0:
                    lista_saida[i].append(lista[j])
                j += 1
    return lista_saida
