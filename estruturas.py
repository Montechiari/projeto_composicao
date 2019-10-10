import numpy as np

# limites para tamanho de secao, em segundos
DURACAO_MAXIMA = 7
LIMITE_SECAO = [30, 60]


class Estrutura:
    '''Estrutura musical.

    Parametros:
    pai - tupla com estrutura superior e ordem na estrutura superior.
    regiao - lista com ponto inferior e dimensoes da regiao.
    contidos - lista de estruturas contidas na estrutura.
    perfis - dicionario de perfis (funcoes trigonometricas).
    atributos - dicionario de atributos auxiliares.
     '''

    def __init__(self, pai=(None, 0),
                 regiao=[(0, 0, 0), (0, 0, 0)],
                 contidos=None,
                 perfis=None,
                 atributos=None):
        self.pai = pai
        self.regiao = regiao

        if contidos is None:
            self.contidos = []
        if perfis is None:
            self.perfis = {}
        if atributos is None:
            self.atributos = {}

    def faz_perfil(self, nome, faixa_de_freq, faixa_de_amp):
        '''Cria elemento no dicionario de pefis.'''
        fase_init_perfil = np.random.rand() * 2 * np.pi
        frequencia = ((np.random.rand() * abs(faixa_de_freq[1] -
                                              faixa_de_freq[0])) +
                      faixa_de_freq[0])
        self.perfis[nome] = (fase_init_perfil, frequencia, faixa_de_amp)


class Peca(Estrutura):
    '''Nome original: Peça'''

    def __init__(self, tecitura, faixa_dinamica):
        super().__init__()
        global LIMITE_SECAO
        self.duracao = np.random.triangular(3, 3.5, 5) * 60
        LIMITE_SECAO = [self.duracao / 6, self.duracao / 3]

        self.regiao[0] = (tecitura[0], faixa_dinamica[0], 0)
        self.regiao[1] = (abs(tecitura[1] - tecitura[0]),
                          abs(faixa_dinamica[1] - faixa_dinamica[0]),
                          self.duracao)

        # Inicializacao de pefis
        self.faz_perfil('dinamica', [0.8 / self.duracao,
                                     1.6 / self.duracao],
                        [faixa_dinamica[0],
                         faixa_dinamica[1]])
        self.faz_perfil('andamento', [1.5 / self.duracao,
                                      2.5 / self.duracao],
                        [0.4, 1.8])
        self.faz_perfil('incerteza', [0.1 / self.duracao,
                                      1.7 / self.duracao],
                        [0, 0.999])
        self.faz_perfil('transposicao', [0.5 / self.duracao,
                                         1.5 / self.duracao],
                        [-10, 14])

        self.cria_secoes()
        self.contornos_basicos = self.constroi_contornos()
        self.contornos_normalizados = []
        for i, chave in enumerate(self.perfis):
            onda = onda_para_escala(self.perfis[chave],
                                    self.contornos_basicos[i])
            self.contornos_normalizados.append(onda)

    def cria_secoes(self):
        qtd_secoes = np.random.randint(int(self.duracao / LIMITE_SECAO[1]),
                                       int(self.duracao / LIMITE_SECAO[0]))
        divisao = self.duracao / qtd_secoes
        divisao_anterior = 0
        fronteiras = []

        for i in range(qtd_secoes - 1):
            novo = ((divisao * (i + 1)) +
                    (((np.random.rand() * 0.4) - 0.2) * divisao))
            fronteiras.append((divisao_anterior, novo))
            divisao_anterior = novo
        fronteiras.append((divisao_anterior, self.duracao))

        for i in range(qtd_secoes):
            self.contidos.append(Secao((self, i),
                                       [(self.regiao[0][0],
                                         self.regiao[0][1],
                                         fronteiras[i][0]),
                                        (self.regiao[1][0],
                                         self.regiao[1][1],
                                         fronteiras[i][1])],
                                       {'idx_refrac': np.random.rand() + 1}))

    def constroi_contornos(self):
        contornos = [[], [], [], []]
        tempo = 0
        fases = [self.perfis[perfil][0] for perfil in self.perfis]

        for i, secao in enumerate(self.contidos[1:]):

            # Desenha onda referente à seção
            while tempo < secao.regiao[0][2]:
                [contornos[j].append(perfil_onda(self.perfis[perf],
                                                 fases[j], tempo))
                 for j, perf in enumerate(self.perfis)]
                tempo += 0.2

            # Acha inclinações (valor abs) no ponto de encontro entre seções.
            inclinacoes = [abs(derivada_onda(self.perfis[perf],
                                             fases[j], tempo))
                           for j, perf in enumerate(self.perfis)]
            # Calcula diferenca no indice de refracao das secoes
            diferenca_refracao = (secao.atributos['idx_refrac'] -
                                  self.contidos[i].atributos['idx_refrac'])
            # Acha novas fases
            fases = [fases[j] + (inclinacoes[j] * diferenca_refracao * 2)
                     for j in range(4)]

        # Faz desenho da ultima secao
        while tempo < self.duracao:
            [contornos[j].append(perfil_onda(self.perfis[perf],
                                             fases[j], tempo))
             for j, perf in enumerate(self.perfis)]
            tempo += 0.2

        return contornos


class Secao(Estrutura):
    def __init__(self, pai, regiao, atributos):
        super().__init__()
        self.pai = pai
        self.regiao = regiao
        self.atributos = atributos
        self.duracao = abs(self.regiao[1][2] - self.regiao[0][2])
    pass


def perfil_onda(perfil, fase, tempo):
    '''Funcao trigonometrica simples.'''
    frequencia_angular = 2 * np.pi * perfil[1]
    return np.sin((frequencia_angular * tempo) + fase)


def derivada_onda(perfil, fase, tempo):
    '''Funcao cosseno, derivada de funcao seno.'''
    frequencia_angular = 2 * np.pi * perfil[1]
    return np.cos((frequencia_angular * tempo) + fase)


def onda_para_escala(perfil, onda):
    '''Transforma onda (lista) de -1 a 1 para a escala original do perfil.'''
    mod_amplitude = abs(perfil[2][1] - perfil[2][0])
    return [(mod_amplitude * ((valor + 1) * 0.5)) + perfil[2][0]
            for valor in onda]


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    pecinha = Piece([42, 87], [25, 115])
    eixo_x = np.arange(0, len(pecinha.contornos_basicos[0]))
    for i in range(4):
        plt.scatter(eixo_x, pecinha.contornos_basicos[i], linewidths=0.01)
    plt.show()
