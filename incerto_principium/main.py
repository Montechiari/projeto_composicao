""" Implementação de Incerto Principium
	em Python. 
"""
from modulo_cadeia import *



TEMPO_MAXIMO = 60
GRAU_INCERTEZA = 15

# CHAVE == 1 -> abre em finale; CHAVE == 2 -> imprime score; CHAVE == 3 -> ambos.
CHAVE = 2

# Inicializa cadeias
cadeia_alturas, cadeia_ritmos = inicia()

# Gera tabelas incertas
altura_incerta = gera_tabela_incerta(cadeia_alturas, GRAU_INCERTEZA)
ritmo_incerto  = gera_tabela_incerta(cadeia_ritmos, GRAU_INCERTEZA)

# Troca tabelas pro ritmo
ritmo_incerto, cadeia_ritmos.t_prob = cadeia_ritmos.t_prob, ritmo_incerto

# Inicia valores
TEMPO_MAXIMO *= 1000
tempo_atual = 0
prox_celula_ritmica = np.random.randint(0, cadeia_ritmos.dimen)
prox_altura = np.random.randint(0, cadeia_alturas.dimen)
lista_de_notas = []



#Corpo principal
while tempo_atual < TEMPO_MAXIMO:
	for i in range(cadeia_ritmos.conteudo[prox_celula_ritmica][0]):
		# Sorteia altura
		ponto_no_tempo = cria_perfil_incerteza('alturas', tempo_atual, TEMPO_MAXIMO)
		lista_interpolada =	interpola_linha(ponto_no_tempo,
											altura_incerta[prox_altura],
											cadeia_alturas.t_prob[prox_altura])
		prox_altura = sorteia_indice(lista_interpolada)

		# Escreve valores de nota
# 			Nota = tupla com t_inicio, duracao, intensidade, altura.
		campo_altura = cadeia_alturas.conteudo[prox_altura][1]
		if cadeia_ritmos.conteudo[prox_celula_ritmica][i+1] < 0:
			campo_duracao = cadeia_ritmos.conteudo[prox_celula_ritmica][i+1] * -1
			campo_intensidade = 0
		else:
			campo_duracao = cadeia_ritmos.conteudo[prox_celula_ritmica][i+1]
			campo_intensidade = 100 # <-ainda nao tem metodo para intensidades
		campo_t_inicio = tempo_atual
		atributos = [campo_t_inicio, campo_duracao, campo_intensidade, float(campo_altura)]
		nova_nota = Nota._make(atributos)

 		# Atualiza tempo maximo ate aqui
		tempo_atual += nova_nota.duracao
		# Adiciona nota em lista
		lista_de_notas.append(nova_nota)

	# Sorteia proxima celula ritmica
	ponto_no_tempo = cria_perfil_incerteza('ritmos', tempo_atual, TEMPO_MAXIMO)
	lista_interpolada = interpola_linha(ponto_no_tempo,
										ritmo_incerto[prox_celula_ritmica],
										cadeia_ritmos.t_prob[prox_celula_ritmica])
	prox_celula_ritmica = sorteia_indice(lista_interpolada)


lista_tgs = temporal_gestalt(lista_de_notas, SEMINIMA, 1/127)
# abre_em_finale(lista_tgs)
# gera_intensidades(lista_tgs)

# if CHAVE & 1: 
# 	abre_em_finale(lista_de_notas)
# if CHAVE & 2:
# 	imprime_score(lista_de_notas)