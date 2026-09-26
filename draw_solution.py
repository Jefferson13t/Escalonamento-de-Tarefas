import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap, Normalize
import numpy as np
from scipy.io import  loadmat
from classes.tarefa import Tarefa
import argparse

def ler_solucao_mat(
    caminho: str
) -> list[list[Tarefa]]:
    """
    Lê uma solução .mat e retorna:

        list[list[Tarefa]]

    A ordem das tarefas dentro de cada máquina é preservada.
    """

    dados = loadmat(caminho)


    if not dados:
        raise ValueError(f"Arquivo de solução não encontrado em {caminho}")

    PT = np.asarray(dados["PT"])
    WE = np.asarray(dados["WE"]).flatten()
    DD = float(np.asarray(dados["DD"]).squeeze())

    SEQ = np.asarray(dados["SEQ"])

    tarefas_por_maquina = []

    for i in range(SEQ.shape[0]):

        tarefas_maquina = []

        for pos in range(SEQ.shape[1]):

            indice = int(SEQ[i, pos])

            # 0 representa posição vazia
            if indice == 0:
                continue

            # O arquivo usa T1, T2, ...
            # Python usa índice 0, 1, ...
            j = indice - 1

            tarefa = Tarefa(
                nome=f"T{indice}",
                w=int(PT[i, j]),
                peso=int(WE[j])
            )

            tarefas_maquina.append(tarefa)

        tarefas_por_maquina.append(tarefas_maquina)

    return tarefas_por_maquina, DD


fig, ax = plt.subplots()

import math

CORES_PENALIDADES = [
            "#00FFA2",
            "#22C55E",
            "#84CC16",
            "#EAB308",
            "#FACC15",
            "#F97316",
            "#EF4444",
            "#DC2626",
        ]

def retornar_cor_por_peso(porcentagem: float) -> str:

    return CORES_PENALIDADES[math.floor(porcentagem * (len(CORES_PENALIDADES) - 1))]

def draw_sequence(tarefas_por_maquina: list[list[Tarefa]], due_date: int, output_img_path: str) -> None:

    ALTURA = 2

    espaco_horizontal_maximo = 0
    espaco_vertical_usado = 0

    penalidade_maxima = max(
        tarefa.peso
        for maquina in tarefas_por_maquina
        for tarefa in maquina
    )

    for idx, maquina in enumerate(tarefas_por_maquina):

        espaco_usado = 0

        altura_maquina = idx * ALTURA
        for tarefa in maquina:

            retangulo = Rectangle(
                (espaco_usado, altura_maquina),  # posição
                tarefa.w, ALTURA,    # largura e altura
                facecolor=retornar_cor_por_peso(tarefa.peso / penalidade_maxima),
                edgecolor="#ffffff"
            )
            ax.add_patch(retangulo)

            centro_texto_h = espaco_usado + tarefa.w / 2
            centro_texto_v = ALTURA / 2 + altura_maquina
            ax.text(
                centro_texto_h, centro_texto_v,
                tarefa.nome,
                color="black",
                fontsize=12,
                ha="center",
                va="center"
            )

            espaco_usado += tarefa.w
            if espaco_horizontal_maximo < espaco_usado:
                espaco_horizontal_maximo = espaco_usado



    espaco_vertical_usado = len(tarefas_por_maquina) * ALTURA

    espaco_horizontal_maximo = max(espaco_horizontal_maximo, due_date)

    cmap = LinearSegmentedColormap.from_list(
        "penalidade",
        CORES_PENALIDADES,
        N=256,
    )
    norm = Normalize(vmin=0, vmax=penalidade_maxima)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar = plt.colorbar(sm, ax=ax, pad=0.02, fraction=0.03)
    cbar.set_label("Penalidade", fontsize=8)
    cbar.ax.tick_params(labelsize=6)

    ax.set_xlim(0, espaco_horizontal_maximo + 1)
    ax.set_ylim(0, espaco_vertical_usado + ALTURA * 2)
    ax.set_aspect("equal")

    # Labels do eixo Y
    ax.set_yticks([
        ALTURA / 2 + i * ALTURA
        for i in range(len(tarefas_por_maquina))
    ])

    ax.set_yticklabels([
        f"M{i + 1}"
        for i in range(len(tarefas_por_maquina))
    ])

    ax.axvline(
        x=due_date,
        color="black",
        linewidth=2,
        linestyle="--"
    )
    ax.text(
        due_date, -1,
        "Due Date",
        color="black",
        fontsize=9,
        ha="center",
        va="center",
    )

    plt.savefig(
        output_img_path,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()


def draw() -> None:
    OUTPUT_DIR = 'outputs'
    OUTPUT_FILE = 'solucao_i5x25'
    OUTPUT_PATH = f"{OUTPUT_DIR}/{OUTPUT_FILE}"

    parser = argparse.ArgumentParser()
    parser.add_argument("solution_file")
    parser.add_argument("solution_img_file", nargs="?")

    args = parser.parse_args()

    solution_file_path = args.solution_file or f"{OUTPUT_PATH}.mat" # Fallback for passado o nome do arquivo

    solution_img_file = args.solution_img_file or f"{solution_file_path.split(sep='.')[0]}.png" # Fallback for passado o nome do arquivo

    tarefas_por_maquina, due_date = ler_solucao_mat(solution_file_path)

    draw_sequence(tarefas_por_maquina, due_date, solution_img_file)

if __name__ == "__main__":
    draw()