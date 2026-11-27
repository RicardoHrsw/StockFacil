import unittest
from decimal import Decimal

from psycopg.errors import ForeignKeyViolation, UniqueViolation

from src.modelos.produto import Produto
from src.servicos.produto_servico import ProdutoServico
from tests.falsos import RegistoFalso


class RepositorioFalso:
    """Faz de conta que é o repositório, com o produto AGUA15 guardado (id 1)."""

    def __init__(self, erro=None):
        self.erro = erro
        self.produtos = {"AGUA15": Produto("AGUA15", "Água", Decimal("0.60"), 1, id_produto=1, stock_atual=12)}
        self.editados = []
        self.desativados = []

    def obter_por_codigo(self, codigo):
        return self.produtos.get(codigo)

    def editar(self, produto):
        if self.erro:
            raise self.erro()
        if produto.id_produto != 1:
            return False
        self.editados.append(produto)
        return True

    def desativar(self, id_produto):
        if id_produto != 1 or id_produto in self.desativados:
            return False
        self.desativados.append(id_produto)
        return True


def dados(**alteracoes):
    """Dados válidos para editar o produto 1; cada teste muda só o que quer experimentar."""
    valores = {"id_produto": 1, "codigo": "AGUA15", "nome": "Água 1,5 L", "preco_venda": "0,65",
               "id_categoria": "1", "descricao": "", "stock_minimo": "10"}
    valores.update(alteracoes)
    return valores


class TestEditarDesativarProduto(unittest.TestCase):
    """Testes a editar e desativar produtos, sem base de dados."""

    def criar_servico(self, repositorio):
        servico = ProdutoServico()
        servico.repositorio = repositorio
        servico.registo = RegistoFalso()
        return servico

    def test_obter_produto_pelo_codigo(self):
        produto = self.criar_servico(RepositorioFalso()).obter("  AGUA15 ")
        self.assertEqual(produto.nome, "Água")

    def test_obter_codigo_vazio(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso()).obter("   ")

    def test_obter_codigo_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso()).obter("NAOEXISTE")

    def test_editar_com_dados_validos(self):
        repositorio = RepositorioFalso()
        produto = self.criar_servico(repositorio).editar(**dados())
        self.assertEqual(produto.preco_venda, Decimal("0.65"))
        self.assertEqual(len(repositorio.editados), 1)

    def test_editar_com_preco_invalido_nao_grava(self):
        repositorio = RepositorioFalso()
        with self.assertRaises(ValueError):
            self.criar_servico(repositorio).editar(**dados(preco_venda="-1"))
        self.assertEqual(len(repositorio.editados), 0)

    def test_editar_produto_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso()).editar(**dados(id_produto=7))

    def test_editar_para_codigo_repetido_da_mensagem_clara(self):
        servico = self.criar_servico(RepositorioFalso(erro=UniqueViolation))
        with self.assertRaises(ValueError) as contexto:
            servico.editar(**dados(codigo="COLA33"))
        self.assertIn("Já existe um produto", str(contexto.exception))

    def test_editar_para_categoria_inexistente_da_mensagem_clara(self):
        servico = self.criar_servico(RepositorioFalso(erro=ForeignKeyViolation))
        with self.assertRaises(ValueError) as contexto:
            servico.editar(**dados(id_categoria="99"))
        self.assertIn("categoria escolhida não existe", str(contexto.exception))

    def test_editar_muda_o_fornecedor(self):
        repositorio = RepositorioFalso()
        self.criar_servico(repositorio).editar(**dados(id_fornecedor="4"))
        self.assertEqual(repositorio.editados[0].id_fornecedor, 4)

    def test_editar_pode_tirar_o_fornecedor(self):
        repositorio = RepositorioFalso()
        self.criar_servico(repositorio).editar(**dados(id_fornecedor=""))
        self.assertIsNone(repositorio.editados[0].id_fornecedor)

    def test_desativar_produto(self):
        repositorio = RepositorioFalso()
        self.criar_servico(repositorio).desativar(1)
        self.assertEqual(repositorio.desativados, [1])

    def test_desativar_duas_vezes_da_erro(self):
        servico = self.criar_servico(RepositorioFalso())
        servico.desativar(1)
        with self.assertRaises(ValueError):
            servico.desativar(1)


if __name__ == "__main__":
    unittest.main()
