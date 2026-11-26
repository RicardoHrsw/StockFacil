import unittest
from decimal import Decimal

from src.modelos.produto import Produto
from src.modelos.utilizador import Utilizador
from src.repositorios.venda_repositorio import StockInsuficiente
from src.servicos.venda_servico import VendaServico

SESSAO = Utilizador("Ana", "ana", "h", 2, "Funcionario", id_utilizador=7)


class ProdutosFalsos:
    """AGUA15: 0,60 € e 10 em stock. CAFE: 1,00 €, 3 em stock e mínimo 5 (stock baixo)."""

    def __init__(self):
        self.produtos = {
            "AGUA15": Produto("AGUA15", "Água", Decimal("0.60"), 1, stock_atual=10, id_produto=1),
            "CAFE": Produto("CAFE", "Café", Decimal("1.00"), 1, stock_minimo=5, stock_atual=3, id_produto=2),
        }

    def obter_por_codigo(self, codigo):
        return self.produtos.get(codigo)

    def listar_stock_baixo(self):
        return [p for p in self.produtos.values() if p.stock_atual <= p.stock_minimo]


class VendasFalsas:
    def __init__(self, falta_stock=False):
        self.falta_stock = falta_stock
        self.gravadas = []

    def registar(self, venda):
        if self.falta_stock:
            raise StockInsuficiente(venda.linhas[0])
        venda.id_venda = 1
        self.gravadas.append(venda)
        return venda


class TestVenda(unittest.TestCase):
    """Registar vendas (RF11 a RF13), sem base de dados."""

    def setUp(self):
        self.vendas = VendasFalsas()
        self.servico = VendaServico()
        self.servico.repositorio = self.vendas
        self.servico.produtos = ProdutosFalsos()

    def carrinho(self, *linhas):
        carrinho = []
        for codigo, quantidade in linhas:
            self.servico.adicionar_linha(carrinho, codigo, quantidade)
        return carrinho

    def test_venda_com_duas_linhas_calcula_o_total(self):
        venda = self.servico.registar(self.carrinho(("AGUA15", "2"), ("CAFE", "1")), SESSAO)
        self.assertEqual(venda.total, Decimal("2.20"))
        self.assertEqual(len(venda.linhas), 2)
        self.assertEqual(venda.id_utilizador, 7)

    def test_linha_guarda_o_preco_do_momento(self):
        carrinho = self.carrinho(("AGUA15", "2"))
        self.assertEqual(carrinho[0].preco_unitario, Decimal("0.60"))

    def test_mesmo_produto_duas_vezes_soma_a_quantidade(self):
        carrinho = self.carrinho(("AGUA15", "2"), ("AGUA15", "3"))
        self.assertEqual(len(carrinho), 1)
        self.assertEqual(carrinho[0].quantidade, 5)

    def test_produto_que_nao_existe_nao_entra_no_carrinho(self):
        carrinho = []
        with self.assertRaises(ValueError):
            self.servico.adicionar_linha(carrinho, "XPTO", "1")
        self.assertEqual(carrinho, [])

    def test_quantidade_zero_nao_entra_no_carrinho(self):
        carrinho = []
        with self.assertRaises(ValueError):
            self.servico.adicionar_linha(carrinho, "AGUA15", "0")
        self.assertEqual(carrinho, [])

    def test_venda_sem_linhas_nao_e_gravada(self):
        with self.assertRaises(ValueError):
            self.servico.registar([], SESSAO)
        self.assertEqual(self.vendas.gravadas, [])

    def test_falta_de_stock_recusa_a_venda_toda(self):
        carrinho = self.carrinho(("AGUA15", "2"), ("CAFE", "5"))
        with self.assertRaises(ValueError) as contexto:
            self.servico.registar(carrinho, SESSAO)
        self.assertIn("pediu 5, só há 3", str(contexto.exception))
        self.assertEqual(self.vendas.gravadas, [])

    def test_soma_de_duas_linhas_acima_do_stock_e_recusada(self):
        carrinho = self.carrinho(("CAFE", "2"), ("CAFE", "2"))
        with self.assertRaises(ValueError):
            self.servico.registar(carrinho, SESSAO)

    def test_vender_todo_o_stock_e_aceite(self):
        venda = self.servico.registar(self.carrinho(("CAFE", "3")), SESSAO)
        self.assertEqual(venda.total, Decimal("3.00"))

    def test_stock_que_acaba_durante_a_gravacao(self):
        self.servico.repositorio = VendasFalsas(falta_stock=True)
        with self.assertRaises(ValueError) as contexto:
            self.servico.registar(self.carrinho(("AGUA15", "1")), SESSAO)
        self.assertIn("não foi gravada", str(contexto.exception))

    def test_alerta_so_dos_produtos_vendidos_com_stock_baixo(self):
        venda = self.servico.registar(self.carrinho(("AGUA15", "1"), ("CAFE", "1")), SESSAO)
        self.assertEqual([p.codigo for p in self.servico.alertas_da_venda(venda)], ["CAFE"])

    def test_sem_alerta_se_o_produto_vendido_tem_stock(self):
        venda = self.servico.registar(self.carrinho(("AGUA15", "1")), SESSAO)
        self.assertEqual(self.servico.alertas_da_venda(venda), [])


if __name__ == "__main__":
    unittest.main()
