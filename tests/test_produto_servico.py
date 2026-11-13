import unittest
from decimal import Decimal

from psycopg.errors import ForeignKeyViolation, UniqueViolation

from src.servicos.produto_servico import ProdutoServico, validar_produto


def produto_valido(**alteracoes):
    """Dados de um produto válido; cada teste muda só o campo que quer experimentar."""
    dados = {"codigo": "AGUA15", "nome": "Água 1,5 L", "preco_venda": "0,60",
             "id_categoria": "1", "descricao": "", "stock_minimo": "10"}
    dados.update(alteracoes)
    return dados


class TestValidarProduto(unittest.TestCase):
    """Testes às validações do produto. Não usam a base de dados."""

    def test_produto_valido(self):
        produto = validar_produto(**produto_valido())
        self.assertEqual(produto.codigo, "AGUA15")
        self.assertEqual(produto.preco_venda, Decimal("0.60"))
        self.assertEqual(produto.stock_minimo, 10)
        self.assertEqual(produto.id_categoria, 1)
        self.assertIsNone(produto.descricao)

    def test_tira_espacos_do_codigo_e_do_nome(self):
        produto = validar_produto(**produto_valido(codigo="  AGUA15 ", nome="  Água  "))
        self.assertEqual(produto.codigo, "AGUA15")
        self.assertEqual(produto.nome, "Água")

    def test_produto_novo_comeca_com_stock_zero(self):
        self.assertEqual(validar_produto(**produto_valido()).stock_atual, 0)

    def test_codigo_vazio_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(codigo="   "))

    def test_codigo_com_31_caracteres_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(codigo="A" * 31))

    def test_codigo_com_30_caracteres_e_aceite(self):
        self.assertEqual(len(validar_produto(**produto_valido(codigo="A" * 30)).codigo), 30)

    def test_nome_vazio_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(nome=""))

    def test_nome_com_101_caracteres_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(nome="N" * 101))

    def test_descricao_com_256_caracteres_e_recusada(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(descricao="d" * 256))

    def test_preco_com_virgula_ou_ponto(self):
        self.assertEqual(validar_produto(**produto_valido(preco_venda="1,20")).preco_venda, Decimal("1.20"))
        self.assertEqual(validar_produto(**produto_valido(preco_venda="1.20")).preco_venda, Decimal("1.20"))

    def test_preco_zero_e_aceite(self):
        self.assertEqual(validar_produto(**produto_valido(preco_venda="0")).preco_venda, 0)

    def test_preco_vazio_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(preco_venda=""))

    def test_preco_com_letras_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(preco_venda="abc"))

    def test_preco_negativo_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(preco_venda="-1"))

    def test_preco_com_3_casas_decimais_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(preco_venda="1,234"))

    def test_preco_infinito_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(preco_venda="Infinity"))

    def test_stock_minimo_vazio_fica_zero(self):
        self.assertEqual(validar_produto(**produto_valido(stock_minimo="")).stock_minimo, 0)

    def test_stock_minimo_decimal_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(stock_minimo="2,5"))

    def test_stock_minimo_negativo_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(stock_minimo="-3"))

    def test_categoria_vazia_e_recusada(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(id_categoria=""))

    def test_categoria_zero_e_recusada(self):
        with self.assertRaises(ValueError):
            validar_produto(**produto_valido(id_categoria="0"))


class RepositorioFalso:
    """Faz de conta que é o repositório, para testar o serviço sem base de dados."""

    def __init__(self, erro=None):
        self.erro = erro
        self.gravados = []

    def criar(self, produto):
        if self.erro:
            raise self.erro()
        produto.id_produto = 1
        self.gravados.append(produto)
        return produto


class TestProdutoServico(unittest.TestCase):
    """Testes ao serviço com um repositório falso."""

    def criar_servico(self, repositorio):
        servico = ProdutoServico()
        servico.repositorio = repositorio
        return servico

    def test_produto_valido_e_gravado(self):
        repositorio = RepositorioFalso()
        produto = self.criar_servico(repositorio).criar(**produto_valido())
        self.assertEqual(produto.id_produto, 1)
        self.assertEqual(len(repositorio.gravados), 1)

    def test_produto_invalido_nao_e_gravado(self):
        repositorio = RepositorioFalso()
        with self.assertRaises(ValueError):
            self.criar_servico(repositorio).criar(**produto_valido(preco_venda="-1"))
        self.assertEqual(len(repositorio.gravados), 0)

    def test_codigo_repetido_da_mensagem_clara(self):
        servico = self.criar_servico(RepositorioFalso(erro=UniqueViolation))
        with self.assertRaises(ValueError) as contexto:
            servico.criar(**produto_valido())
        self.assertIn("Já existe um produto", str(contexto.exception))

    def test_categoria_inexistente_da_mensagem_clara(self):
        servico = self.criar_servico(RepositorioFalso(erro=ForeignKeyViolation))
        with self.assertRaises(ValueError) as contexto:
            servico.criar(**produto_valido(id_categoria="99"))
        self.assertIn("categoria escolhida não existe", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
