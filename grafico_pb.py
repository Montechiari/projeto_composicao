import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle


def imprime_plot(partitura, curvas, nome):

    fig = plt.figure(figsize=(10, 2), dpi=740)
    eixo_1 = fig.add_subplot(111)
    # eixo_2 = fig.add_subplot(212)
    mapa_cor = cmx.ScalarMappable(colors.Normalize(0, 127, True),
                                  plt.cm.Greys)

    # _________________________________________________________ PRIMEIRO EIXO
    for nota in partitura:
        if nota[2] != 0:
            eixo_1.add_patch(Rectangle((nota[0], nota[1]),
                                       nota[3],
                                       1,
                                       facecolor=mapa_cor.to_rgba(nota[2]),
                                       edgecolor='black',
                                       linewidth=0.1))

    # for perfil in curvas:
    #     eixo_2.plot(range(len(perfil)), perfil, ls='--', linewidth=0.2)

    eixo_1.tick_params('both',
                       bottom=False,
                       left=False,
                       labelbottom=False,
                       labelleft=False)

    # eixo_2.tick_params('both',
    #                    bottom=False,
    #                    left=False,
    #                    labelbottom=False,
    #                    labelleft=False)

    eixo_1.autoscale(enable=True, axis='both')
    # eixo_2.autoscale(enable=True, axis='both')

    eixo_1.set_ylim([46, 91])
    # _________________________________________________________ PRIMEIRO EIXO

    plt.tight_layout(0, h_pad=None, w_pad=None)
    plt.savefig(nome, pad_inches=0)
    # plt.show()
