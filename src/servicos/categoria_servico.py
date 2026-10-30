from psycopg.errors import UniqueViolation

from src.modelos.categoria import Categoria
from src.repositorios.categoria_repositorio import CategoriaRepositorio

TAMANHO_MAXIMO_NOME = 50
TAMANHO_MAXIMO_DESCRICAO = 255


def validar_categoria(nome, descricao):
    nome = (nome or "").strip()
    descricao = (descricao or "").strip()

    if nome == "":
        raise ValueError("O nome azio.")
    if len(nome) > TAMANHO_MAXIMO_NOME:
        raise ValueError(f"O nomeO_MAXIMO_NOME} caracteres.")
    if len(descricao) > TAMANHO_MAXIMO_DESCRICAO:
        raise ValueError(f"A descAMANHO_MAXIMO_DESCRICAO}
caracteres.")

    if descricao == "":
        descricao = None  # descrLL) na base de dados

    return nome, descricao


class CategoriaServico:

    def __init__(self):
        self.repositorio = CategoriaRepositorio()

    def listar(self):
        return self.repositorio.listar()

    def criar(self, nome, descricao=None):
        nome, descricao = validar_categoria(nome, descricao)
        try:
            return self.repositorio.criar(Categoria(nome, descricao))
        except UniqueViolation:
            raise ValueError(f"Já existe uma categoria chamada '{nome}'.")