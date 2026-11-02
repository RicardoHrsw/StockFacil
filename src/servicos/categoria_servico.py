from psycopg.errors import UniqueViolation

from src.modelos.categoria import Categoria
from src.repositorios.categoria_repositorio import CategoriaRepositorio

TAMANHO_MAXIMO_NOME = 50
TAMANHO_MAXIMO_DESCRICAO = 255


def validar_categoria(nome, descricao):
    """Limpa e valida os dados. Devolve o nome e a descrição prontos a gravar.

    Não usa a base de dados, por isso pode ser testada sozinha.
    """
    nome = (nome or "").strip()
    descricao = (descricao or "").strip()

    if nome == "":
        raise ValueError("O nome da categoria não pode estar vazio.")
    if len(nome) > TAMANHO_MAXIMO_NOME:
        raise ValueError(f"O nome não pode ter mais de {TAMANHO_MAXIMO_NOME} caracteres.")
    if len(descricao) > TAMANHO_MAXIMO_DESCRICAO:
        raise ValueError(f"A descrição não pode ter mais de {TAMANHO_MAXIMO_DESCRICAO} caracteres.")

    if descricao == "":
        descricao = None  

    return nome, descricao


class CategoriaServico:
    """Regras de negócio das categorias."""

    def __init__(self):
        self.repositorio = CategoriaRepositorio()

    def listar(self):
        """Devolve todas as categorias, ordenadas por nome."""
        return self.repositorio.listar()

    def criar(self, nome, descricao=None):
        """Valida os dados e grava uma categoria nova."""
        nome, descricao = validar_categoria(nome, descricao)
        try:
            return self.repositorio.criar(Categoria(nome, descricao))
        except UniqueViolation:
            raise ValueError(f"Já existe uma categoria chamada '{nome}'.")
