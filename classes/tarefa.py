class Tarefa:
    def __init__(self, nome: str, w: int,  peso: int) -> None:
        self.nome = nome
        self.w = w
        self.peso = peso

    def __str__(self) -> str:
        return f"nome: {self.nome} | custo: {self.w} | penalidade: {self.peso}"
    
    def __repr__(self) -> str:
        return self.__str__()