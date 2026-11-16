from psycopg.errors import ForeignKeyViolation, UniqueViolation
from src.modelos.categoria import Categoria
from src.repositorios.categoria_repositorio import CategoriaRepositorio

TAMANHO_MAXIMO_NOME = 50
TAMANHO_MAXIMO_DESCRICAO = 255


def validar_categoria(nome, descricao):
    """Limpa e valida os dados. Devolve o nome e a descrição prontos a gravar"""
    
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


def converter_id_categoria(valor):
    """Confirma que o número da categoria é um inteiro positivo."""
    try:
        id_categoria = int(str(valor).strip())
    except ValueError:
        raise ValueError("Escolha uma categoria da lista, pelo número.")
    if id_categoria <= 0:
        raise ValueError("Escolha uma categoria da lista, pelo número.")
    return id_categoria


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

    def obter(self, id_categoria):
        """Devolve a categoria com este número, ou dá erro se não existir."""
        id_categoria = converter_id_categoria(id_categoria)
        categoria = self.repositorio.obter(id_categoria)
        if categoria is None:
            raise ValueError(f"Não existe nenhuma categoria com o número {id_categoria}.")
        return categoria

    def editar(self, id_categoria, nome, descricao=None):
        """Valida os dados novos e atualiza a categoria."""
        id_categoria = converter_id_categoria(id_categoria)
        nome, descricao = validar_categoria(nome, descricao)
        categoria = Categoria(nome, descricao, id_categoria)
        try:
            encontrada = self.repositorio.editar(categoria)
        except UniqueViolation:
            raise ValueError(f"Já existe uma categoria chamada '{nome}'.")
        if not encontrada:
            raise ValueError(f"Não existe nenhuma categoria com o número {id_categoria}.")
        return categoria

    def apagar(self, id_categoria):
        """Apaga a categoria, desde que não tenha produtos associados."""
        id_categoria = converter_id_categoria(id_categoria)
        try:
            encontrada = self.repositorio.apagar(id_categoria)
        except ForeignKeyViolation:
            raise ValueError("Não é possível apagar esta categoria porque tem produtos associados.")
        if not encontrada:
            raise ValueError(f"Não existe nenhuma categoria com o número {id_categoria}.")
