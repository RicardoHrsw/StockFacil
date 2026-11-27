import unittest

from psycopg.errors import ForeignKeyViolation, UniqueViolation

from src.modelos.categoria import Categoria
from src.servicos.categoria_servico import CategoriaServico
from tests.falsos import RegistoFalso


class RepositorioFalso:
    """Faz de conta que é o repositório, com a categoria 1 - Bebidas guardada."""

    def __init__(self, erro=None):
        self.erro = erro
        self.categorias = {1: Categoria("Bebidas", "Águas e sumos", 1)}
        self.editadas = []
        self.apagadas = []

    def obter(self, id_categoria):
        return self.categorias.get(id_categoria)

    def editar(self, categoria):
        if self.erro:
            raise self.erro()
        if categoria.id_categoria not in self.categorias:
            return False
        self.editadas.append(categoria)
        return True

    def apagar(self, id_categoria):
        if self.erro:
            raise self.erro()
        if id_categoria not in self.categorias:
            return False
        self.apagadas.append(id_categoria)
        return True


class TestEditarApagarCategoria(unittest.TestCase):
    """Testes a editar e apagar categorias, sem base de dados."""

    def criar_servico(self, repositorio):
        servico = CategoriaServico()
        servico.repositorio = repositorio
        servico.registo = RegistoFalso()
        return servico

    def test_obter_categoria_que_existe(self):
        categoria = self.criar_servico(RepositorioFalso()).obter("1")
        self.assertEqual(categoria.nome, "Bebidas")

    def test_obter_categoria_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso()).obter("7")

    def test_numero_invalido_e_recusado(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso()).obter("abc")

    def test_editar_com_dados_validos(self):
        repositorio = RepositorioFalso()
        categoria = self.criar_servico(repositorio).editar("1", "  Bebidas frias ", "")
        self.assertEqual(categoria.nome, "Bebidas frias")
        self.assertIsNone(categoria.descricao)
        self.assertEqual(len(repositorio.editadas), 1)

    def test_editar_com_nome_vazio_nao_grava(self):
        repositorio = RepositorioFalso()
        with self.assertRaises(ValueError):
            self.criar_servico(repositorio).editar("1", "   ", None)
        self.assertEqual(len(repositorio.editadas), 0)

    def test_editar_categoria_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso()).editar("7", "Nova", None)

    def test_editar_para_nome_repetido_da_mensagem_clara(self):
        servico = self.criar_servico(RepositorioFalso(erro=UniqueViolation))
        with self.assertRaises(ValueError) as contexto:
            servico.editar("1", "Material Escolar", None)
        self.assertIn("Já existe", str(contexto.exception))

    def test_apagar_categoria_sem_produtos(self):
        repositorio = RepositorioFalso()
        self.criar_servico(repositorio).apagar("1")
        self.assertEqual(repositorio.apagadas, [1])

    def test_apagar_categoria_com_produtos_da_mensagem_clara(self):
        servico = self.criar_servico(RepositorioFalso(erro=ForeignKeyViolation))
        with self.assertRaises(ValueError) as contexto:
            servico.apagar("1")
        self.assertIn("tem produtos associados", str(contexto.exception))

    def test_apagar_categoria_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso()).apagar("7")


if __name__ == "__main__":
    unittest.main()
