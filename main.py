import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import argparse
import numpy as np
from scipy.io import savemat, loadmat
from classes.tarefa import Tarefa


def salvar_solucao_mat(
    caminho: str,
    tarefas_por_maquina: list[list[Tarefa]],
    PT: np.ndarray,
    WE: np.ndarray,
    DD: np.ndarray,
) -> None:
    """
        Salva a solução em um arquivo MATLAB .mat.

        PT, WE e DD mantêm o mesmo formato do arquivo de entrada.
        SEQ contém o sequenciamento das tarefas por máquina.

        As tarefas no SEQ são armazenadas usando índices começando em 1,
        seguindo a convenção do MATLAB.
    """

    # Número máximo de tarefas em uma máquina
    max_tarefas = max(
        len(tarefas)
        for tarefas in tarefas_por_maquina
    )

    # Preencher com 0.
    # 0 significa que não há tarefa naquela posição.
    SEQ = np.zeros(
        (len(tarefas_por_maquina), max_tarefas),
        dtype=np.uint16
    )

    for i, tarefas in enumerate(tarefas_por_maquina):

        for pos, tarefa in enumerate(tarefas):

            # Tarefa 'T1' -> índice 1
            # Tarefa 'T2' -> índice 2
            # etc.
            indice = int(
                tarefa.nome.replace("T", "")
            )

            SEQ[i, pos] = indice

    # Salvar mantendo a estrutura MATLAB
    dados = {
        "PT": np.asarray(PT),
        "WE": np.asarray(WE),
        "DD": np.asarray(DD),
        "SEQ": SEQ,
    }

    savemat(caminho, dados)


def solve(pt, we, dd) -> list[list[Tarefa]] :
    """
        Instancia um solver, cria as restrições e resolve um problema

        Args:
            pt: Tempo que a máquina i leva para processar a tarefa j
            we: Penalidade por atraso da tarefa j. Indice [j]
            dd: Due Date. Número escalar
        Outputs:
            tarefas_por_maquina: Matriz em que cada posição é uma lista das tarefas que serão executadas por aquela máquina

    """

    opt = SolverFactory('highs')

    model = pyo.ConcreteModel()

    # Pega o maior tempo de processamento que sera usado como limite superior par ao horizonte de escalonamento
    H = 224 #max(sum([linha for linha in pt])) TODO: Inverter os indices

    # Conjuntos
    # Numero de máquinas
    M = len(pt)

    # Numero de Tarefas
    J = len(pt[0])

    # Due Date
    d = dd
    # Variáveis

    # x_ij = 1 se a tarefa j for atribuída à máquina i
    xij = [
        (i, j)
        for i in range(M)
        for j in range(J)
    ]

    model.x = pyo.Var(xij, within=pyo.Binary)

    # y_ijk = 1 se a tarefa j preceder k na máquina i
    yijk = [
        (i, j, k)
        for i in range(M)
        for j in range(J)
        for k in range(j + 1, J)
    ]

    model.y = pyo.Var(
        yijk,
        within=pyo.Binary,
    )

    # S_j = instante de início da tarefa j
    Sj = [j for j in range(J)]

    model.S = pyo.Var(
        Sj,
        within=pyo.NonNegativeIntegers,
    )

    # C_j = instante de conclusão da tarefa j
    Cj = [j for j in range(J)]

    model.C = pyo.Var(
        Cj,
        within=pyo.NonNegativeIntegers,
    )

    # T_j = atraso da tarefa j
    Tj = [j for j in range(J)]

    model.T = pyo.Var(
        Tj,
        within=pyo.NonNegativeIntegers,
    )


    # Cmax = makespan
    model.Cmax = pyo.Var(
        within=pyo.NonNegativeIntegers,
    )

    # Funções objetivo

    # Minimizar Cmax
    def fo1(model):
        return model.Cmax


    # Minimizar atraso ponderado
    def fo2(model):
        return pyo.quicksum(
            we[j] * model.T[j]
            for j in range(J)
        )

    def fo(model):
        return fo1(model) + fo2(model)

    # Escolha da função objetivo
    model.o = pyo.Objective(
        rule=fo,
        sense=pyo.minimize
    )


    # Restrições

    model.c = pyo.ConstraintList()

    # 1. Alocação única
    # Cada tarefa deve ser atribuída a exatamente uma máquina.

    for j in range(J):
        model.c.add(
            pyo.quicksum(
                model.x[i, j]
                for i in range(M)
            ) == 1
        )


    # 2. Tempo de conclusão
    for j in range(J):
        model.c.add(
            model.C[j] ==
            model.S[j] +
            pyo.quicksum(
                pt[i][j] * model.x[i, j]
                for i in range(M)
            )
        )

    # 3. Makespan
    # Cmax >= C_j para toda tarefa j
    for j in range(J):
        model.c.add(
            model.Cmax >= model.C[j]
        )


    # 4. Atraso
    # T_j >= C_j - d_j
    # T_j >= 0
    # Como T_j já é NonNegativeIntegers, a segunda restrição
    # é implicitamente garantida, mas pode ser mantida.
    for j in range(J):
        model.c.add(
            model.T[j] >= model.C[j] - d
        )
        model.c.add(
            model.T[j] >= 0
        )


    # 5. Ligação entre alocação e sequenciamento
    # Para cada par j,k em uma máquina i:
    # y_ijk = 1 -> j precede k
    # y_ijk = 0 -> k precede j, quando ambas estão na máquina i

    for i in range(M):
        for j in range(J):
            for k in range(j + 1, J):

                # Se j e k estão na máquina i, uma delas
                # deve preceder a outra.
                model.c.add(
                    model.y[i, j, k] <= model.x[i, j]
                )

                model.c.add(
                    model.y[i, j, k] <= model.x[i, j]
                )

                model.c.add(
                    model.y[i, j, k] >= model.x[i, j] + model.x[i, j] - 1
                )



    # 6. Não sobreposição
    # Se j e k estão na mesma máquina:

    # y_ijk = 1:
    #     S_k >= C_j
    # y_ijk = 0:
    #     S_j >= C_k
    # Big-M / Big-H

    for i in range(M):
        for j in range(J):
            for k in range(j + 1, J):

                # j e k estão na mesma máquina i
                # e y = 1 => j antes de k
                model.c.add(
                    model.S[k] >=
                    model.C[j]
                    - H * (1 - model.y[i, j, k])
                    - H * (1 - model.x[i, j])
                    - H * (1 - model.x[i, k])
                )

                # y = 0 => k antes de j
                model.c.add(
                    model.S[j] >=
                    model.C[k]
                    - H * model.y[i, j, k]
                    - H * (1 - model.x[i, j])
                    - H * (1 - model.x[i, k])
                )



    # 7. Horizonte de planejamento
    for j in range(J):

        model.c.add(
            model.S[j] >= 0
        )

        model.c.add(
            model.S[j] <= H
        )

        model.c.add(
            model.C[j] >= 0
        )

        model.c.add(
            model.C[j] <= H
        )


    # Resolver
    result = opt.solve(model, tee=True)

    print("Otimização completa.")

    # Resultados
    print("Cmax =", pyo.value(model.Cmax))

    # for j in range(J):
    #     print(
    #         f"Tarefa {j}: "
    #         f"S={pyo.value(model.S[j])}, "
    #         f"C={pyo.value(model.C[j])}, "
    #         f"T={pyo.value(model.T[j])}"
    #     )

    # for i in range(M):
    #     for j in range(J):
    #         if pyo.value(model.x[i, j]) > 0.5:
    #             print(
    #                 f"Tarefa {j} -> Máquina {i}"
    #             )

    # Saída: tarefas por máquina
    tarefas_por_maquina = []

    for i in range(M):

        tarefas_maquina = []

        # Tarefas atribuídas à máquina i
        tarefas_i = [
            j
            for j in range(J)
            if pyo.value(model.x[i, j]) > 0.5
        ]

        # Ordenar pela sequência determinada pelo instante de início
        tarefas_i.sort(
            key=lambda j: pyo.value(model.S[j])
        )

        for j in tarefas_i:

            tarefa = Tarefa(
                nome=f"T{j + 1}",
                w=pt[i][j],
                peso=we[j]
            )

            tarefas_maquina.append(tarefa)

        tarefas_por_maquina.append(tarefas_maquina)

    return tarefas_por_maquina


def main() -> None:
    # Buscar dados de um arquivo .mat
    INPUT_DIR = 'inputs'
    INPUT_FILE = 'i5x25.mat'
    INPUT_PATH = f"{INPUT_DIR}/{INPUT_FILE}"

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("solution_file")
    args = parser.parse_args()

    input_path = args.input_file or INPUT_PATH # Fallback for passado o nome do arquivo

    
    mat = loadmat(input_path)

    if not mat:
        raise ValueError("Arquivo de input não encontrado")

    pt = mat['PT'] # Tempo que a máquina j leva para processar a tarefa i. Indice [j][i]
    we = mat['WE'][0] # Penalidade por atraso da tarefa j. Indice [j]
    dd = mat['DD'] # Due Date. Número escalar

    # resolver 
    tarefas_por_maquina = solve(pt, we, dd)

    # Salvar solução em um arquivo .mat
    OUTPUT_DIR = 'outputs'
    OUTPUT_FILE = INPUT_FILE
    OUTPUT_PATH = f"{OUTPUT_DIR}/{OUTPUT_FILE}.mat"

    solution_file_path = args.solution_file or OUTPUT_PATH # Fallback for passado o nome do arquivo

    salvar_solucao_mat(
        solution_file_path,
        tarefas_por_maquina,
        pt,
        we,
        dd
    )

if __name__ == "__main__":
    main()