import argparse
import random
from scipy.io import savemat

def generate_instance(M: int, J: int, d: int, path: str) -> None:
    """
        Gera uma instancia com valores aleatórios dado uma quantidade de máquinas, tarefas, e um due_date 
        Args:
            M: Numero de maquinas
            J: Numero de tarefas
            d: Due Date
            path: Nome do arquivo .mat gerado
    """

    PT = []

    MAX_COST = 20
    MAX_WEIGHT = 30

    for _ in range(M):
        custo_tarefas = [random.randint(1, MAX_COST) for _ in range(J)]
        PT.append(custo_tarefas)

    WE = [random.randint(1, MAX_WEIGHT) for _ in range(J)]

    DD = [d]

    dados = {
        'PT': PT,
        'WE': WE, 
        'DD': DD,
    }

    savemat(path, dados)


def main(): 
    parser = argparse.ArgumentParser()
    parser.add_argument("M")
    parser.add_argument("J")
    parser.add_argument("d")
    parser.add_argument("path")

    args = parser.parse_args()

    M = int(args.M)
    J = int(args.J)
    d = int(args.d)
    path = args.path

    generate_instance(M, J, d, path)

if __name__ == "__main__":
    main()



# examplo_input_format = {
#     '__header__': b'MATLAB 5.0 MAT-file, Platform: MACI64, Created on: Sat Apr 19 20:03:34 2014', 
#     '__version__': '1.0', 
#     '__globals__': [], 
#     'PT': array(
#         [
#             [ 2,  8,  8,  4,  9,  3,  9, 10,  9,  6, 10,  4,  9,  4,  2,  5, 7,  6,  1,  3,  1, 10,  6,  2,  1],
#             [ 1,  3,  8,  9, 10,  3,  1,  6,  8,  1, 10,  7,  5,  7,  9,  8, 8,  9,  5,  2,  6,  8,  2,  1,  9],
#             [ 4,  2,  8, 10,  7,  4,  1,  4,  1,  4,  6,  6,  3,  3, 10,  2, 7,  1,  8,  7,  7,  4,  9,  1,  3], 
#             [ 7,  1,  4,  4,  5,  3,  8,  9,  1, 10,  5,  2,  6,  8,  8,  6, 1,  8,  8,  9,  9,  4,  3,  6, 10], 
#             [ 8,  5,  1,  5,  3,  8,  3,  6,  9,  6,  9,  6,  2,  1,  6,  9, 8,  9, 10,  4, 10,  9,  8,  5,  8]
#         ], 
#         dtype=uint8), 
#     'WE': array(
#         [
#             [ 8,  5,  7, 10,  2,  5,  2,  8, 10,  6,  3,  7,  2,  7,  2, 10, 1,  1,  6,  1,  1,  9,  5, 10,  3]
#         ], 
#         dtype=uint8), 
#     'DD': array(
#         [
#             [6]
#         ], 
#         dtype=uint8)
# }