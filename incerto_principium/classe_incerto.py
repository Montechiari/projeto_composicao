from incerto_principium import modulo_cadeia as mcad
import numpy as np

GRAU_INCERTEZA = 20


class IncertoPrincipium:
    def __init__(self):
        self.cadeia_alturas, self.cadeia_ritmos = mcad.inicia()
        self.altura_incerta = mcad.gera_tabela_incerta(self.cadeia_alturas,
                                                       GRAU_INCERTEZA)
        self.ritmo_incerto = mcad.gera_tabela_incerta(self.cadeia_ritmos,
                                                      GRAU_INCERTEZA)

        # Troca tabelas
        self.ritmo_incerto, self.cadeia_ritmos.t_prob = self.cadeia_ritmos.t_prob, self.ritmo_incerto

        self.prox_cel_ritmica = np.random.randint(0, self.cadeia_ritmos.dimen)
        self.prox_altura = np.random.randint(0, self.cadeia_alturas.dimen)
        self.idx_cel_ritmica = 0

    def proxima_nota(self, incerteza):
        if self.idx_cel_ritmica == self.cadeia_ritmos.conteudo[self.prox_cel_ritmica][0]:
            lista_interpolada_ritmo = mcad.interpola_linha(incerteza/15,
                                                           self.cadeia_ritmos.t_prob[self.prox_cel_ritmica],
                                                           self.ritmo_incerto[self.prox_cel_ritmica])
            self.prox_cel_ritmica = mcad.sorteia_indice(lista_interpolada_ritmo)
            self.idx_cel_ritmica = 0

        duracao = self.cadeia_ritmos.conteudo[self.prox_cel_ritmica][self.idx_cel_ritmica + 1]
        self.idx_cel_ritmica += 1

        lista_interpolada_altura = mcad.interpola_linha(incerteza/15,
                                                        self.cadeia_alturas.t_prob[self.prox_altura],
                                                        self.altura_incerta[self.prox_altura])
        self.prox_altura = mcad.sorteia_indice(lista_interpolada_altura)
        altura = self.cadeia_alturas.conteudo[self.prox_altura][1]

        if duracao < 0:
            intensidade = 0
            duracao = abs(duracao)
        else:
            intensidade = 1

        return [altura, intensidade, duracao / 1000]
