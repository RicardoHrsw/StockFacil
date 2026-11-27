import unittest
from decimal import Decimal

from psycopg.errors import ForeignKeyViolation

from src.modelos.produto import Produto
from src.modelos.utilizador import Utilizador
from src.servicos.entrada_servico import EntradaServico, converter_quantidade
from tests.falsos import RegistoFalso

SESSAO = Utilizador("Ana", "ana", "h", 2, "Funcionario", id_utilizador=7)


class TestQuantidade(unittest.TestCase):
    """A quantidade de uma entrada tem de ser um inteiro maior que 0."""

    def test_quantidade_valida(self):
        self.assertEqual(converter_quantidade(" 12 "), 12)

    def test_quantidade_zero_e_recusada(self):
        with self.assertRaises(ValueError):
            converter_quantidade("0")

    def test_quantidade_negativa_e_recusada(self):
        with self.assertRaises(ValueError):
            converter_quantidade("-3")

    def test_quantidade_decimal_e_recusada(self):
        with self.assertRaises(ValueError):
            converter_quantidade("2,5")

    def test_quantidade_vazia_e_recusada(self):
        with self.assertRaises(ValueError):
            converter_quantidade("")

    def test_quantidade_enorme_e_recusada(self):
        with self.assertRaises(ValueError):
            converter_quantidade("100001")


class ProdutosFalsos:
    """AGUA15 tem o fornecedor 1; CAFE não tem fornecedor."""

    def obter_por_codigo(self, codigo):
        produtos = {
            "AGUA15": Produto("AGUA15", "Água", Decimal("0.60"), 1, id_fornecedor=1, stock_atual=10, id_produto=1),
            "CAFE": Produto("CAFE", "Café", Decimal("1.00"), 1, stock_atual=0, id_produto=2),
        }
        return produtos.get(codigo)


class EntradasFalsas:
    def __init__(self, erro=None, desativado=False):
        self.erro = erro
        self.desativado = desativado
        self.gravadas = []

    def registar(self, entrada):
        if self.erro:
            raise self.erro()
        if self.desativado:
            return None
        self.gravadas.append(entrada)
        return 10 + entrada.quantidade


class TestRegistarEntrada(unittest.TestCase):
    """Registar uma entrada de stock (RF10), sem base de dados."""

    def criar_servico(self, entradas=None):
        servico = EntradaServico()
        servico.repositorio = entradas or EntradasFalsas()
        servico.registo = RegistoFalso()
        servico.produtos = ProdutosFalsos()
        return servico

    def test_entrada_valida_sobe_o_stock(self):
        servico = self.criar_servico()
        entrada, produto, novo_stock = servico.registar("AGUA15", "1", "12", "0,35", SESSAO)
        self.assertEqual(novo_stock, 22)
        self.assertEqual(entrada.preco_custo, Decimal("0.35"))
        self.assertEqual(entrada.id_utilizador, 7)

    def test_fornecedor_em_branco_usa_o_do_produto(self):
        entrada, _, _ = self.criar_servico().registar("AGUA15", "", "5", "0,35", SESSAO)
        self.assertEqual(entrada.id_fornecedor, 1)

    def test_produto_sem_fornecedor_obriga_a_escolher(self):
        with self.assertRaises(ValueError) as contexto:
            self.criar_servico().registar("CAFE", "", "5", "0,80", SESSAO)
        self.assertIn("não tem fornecedor", str(contexto.exception))

    def test_produto_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.criar_servico().registar("XPTO", "1", "5", "1", SESSAO)

    def test_preco_de_custo_vazio_da_mensagem_clara(self):
        with self.assertRaises(ValueError) as contexto:
            self.criar_servico().registar("AGUA15", "1", "5", "", SESSAO)
        self.assertIn("preço de custo", str(contexto.exception))

    def test_dados_invalidos_nao_gravam_nada(self):
        entradas = EntradasFalsas()
        with self.assertRaises(ValueError):
            self.criar_servico(entradas).registar("AGUA15", "1", "0", "0,35", SESSAO)
        self.assertEqual(entradas.gravadas, [])

    def test_fornecedor_que_nao_existe_da_mensagem_clara(self):
        with self.assertRaises(ValueError) as contexto:
            self.criar_servico(EntradasFalsas(erro=ForeignKeyViolation)).registar("AGUA15", "99", "5", "1", SESSAO)
        self.assertIn("fornecedor escolhido não existe", str(contexto.exception))

    def test_produto_desativado_entretanto(self):
        with self.assertRaises(ValueError):
            self.criar_servico(EntradasFalsas(desativado=True)).registar("AGUA15", "1", "5", "1", SESSAO)


if __name__ == "__main__":
    unittest.main()
