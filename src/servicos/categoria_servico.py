from src.modelos.categoria import Categoria
from src.repositorios.categoria_repositorio import CategoriaRepositorio

class CategoriaServico:
    def __init__(self):
        self.repositorio = CategoriaRepositorio()

    def listar(self):
        return self.repositorio.listar()

    def criar(self, nome, descricao=None):
        nome = nome.strip()
        self._validar_nome(nome)
        return self.repositorio.criar(Categoria(nome, descricao))

    def _validar_nome(self, nome):
        if nome == "":
            raise ValueError("O nome da categoria não pode estar vazio.")
        if len(nome) > 50:
            raise ValueError("O nome da categoria não pode ter mais de 50 caracteres.")
        for categoria in self.repositorio.listar():
            if categoria.nome.lower() == nome.lower():
                raise ValueError(f"Já existe uma categoria chamada '{nome}'.")