import argparse
from pathlib import Path

import numpy as np
from scipy.io import loadmat


def print_matrix(name: str, matrix: np.ndarray) -> None:
    """Imprime uma matriz com índices de máquinas e tarefas."""
    rows, cols = matrix.shape

    print(f"\n{'=' * 12} {name} {'=' * 12}")
    print(f"{'Máquina':<10}", end="")

    for j in range(cols):
        print(f"{'T' + str(j + 1):>5}", end="")

    print()
    print("-" * (10 + 5 * cols))

    for i in range(rows):
        print(f"{'M' + str(i + 1):<10}", end="")

        for j in range(cols):
            print(f"{matrix[i, j]:>5}", end="")

        print()


def print_vector(name: str, values: np.ndarray, prefix: str) -> None:
    """Imprime um vetor com os índices das tarefas."""
    values = np.asarray(values).flatten()

    print(f"\n{'=' * 12} {name} {'=' * 12}")

    for j, value in enumerate(values):
        print(f"{prefix}{j + 1:<4} : {value:g}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Visualiza uma instância do problema de escalonamento."
    )
    parser.add_argument("input_file", help="Caminho para o arquivo .mat")
    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.is_file():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {input_path}"
        )

    mat = loadmat(input_path)

    pt = np.asarray(mat["PT"])
    we = np.asarray(mat["WE"]).flatten()
    dd = np.asarray(mat["DD"]).item()

    maquinas, tarefas = pt.shape

    if len(we) != tarefas:
        raise ValueError(
            f"WE possui {len(we)} valores, mas PT possui {tarefas} tarefas."
        )

    print("\n" + "#" * 45)
    print("       INSTÂNCIA DE ESCALONAMENTO")
    print("#" * 45)

    print(f"\nArquivo     : {input_path}")
    print(f"Maquinas    : {maquinas}")
    print(f"Tarefas     : {tarefas}")
    print(f"Due date    : {dd:g}")

    print_matrix("TEMPOS DE PROCESSAMENTO (PT)", pt)
    print_vector("PESOS DE ATRASO (WE)", we, "T")
    print(f"\n{'=' * 12} DUE DATE (DD) {'=' * 12}")
    print(f"Data de entrega comum: {dd:g}")

    print("\n" + "#" * 45)
    print("             FIM DA INSTÂNCIA")
    print("#" * 45)


if __name__ == "__main__":
    main()