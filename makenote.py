''' Context manager de envio de mensagem midi, criado para subtituir
o makenote do Pure Data. (Chamado por meusthreads.py)
Duracao aqui eh em segundos!'''

from mido import Message, open_output, get_output_names
from time import sleep
import threading


class Protocolo_MIDI:
    def __enter__(self):
        return self

    def iniciar(self):
        porta = get_output_names()
        porta = porta[0]
        print('porta midi aberta:', porta)
        self.porta_out = open_output(porta)

    def makenote(self, altura, intensidade, duracao, canal=0):
        self.porta_out.send(Message('note_on', note=altura,
                                    velocity=intensidade,
                                    channel=canal))
        sleep(duracao)
        self.porta_out.send(Message('note_off', note=altura,
                                    channel=canal))

    def finalizar(self):
        print('porta midi fechada.')
        self.porta_out.close()


class Protocolo_MIDI2:
    def __enter__(self):
        return self

    def iniciar(self):
        porta = get_output_names()
        porta = porta[0]
        print('porta midi aberta:', porta)
        self.porta_out = open_output(porta)

    def makenote(self, altura, intensidade, duracao, canal=1):
        nota = nota_thread(self.porta_out, altura, intensidade, duracao, canal)
        nota.start()

    def finalizar(self):
        print('porta midi fechada.')
        self.porta_out.close()


class nota_thread(threading.Thread):
    def __init__(self, porta, altura, intensidade, duracao, canal=1):
        threading.Thread.__init__(self)
        self.altura = altura
        self.intensidade = intensidade
        self.duracao = duracao
        self.canal = canal
        self.porta = porta

    def run(self):
        self.porta.send(Message('note_on', note=self.altura,
                                velocity=self.intensidade,
                                channel=self.canal))
        sleep(self.duracao)
        self.porta.send(Message('note_off', note=self.altura,
                                channel=self.canal))


if __name__ == '__main__':

    with Protocolo_MIDI() as midis:
        for i in range(11):
            midis.makenote(60 + i, 120, 1)
