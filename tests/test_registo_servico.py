import unittest
from decimal import Decimal

import bcrypt

from src import sessao
from src.modelos.produto import Produto
from src.modelos.utilizador import Utilizador
from src.servicos.autenticacao_servico import AutenticacaoServico
from src.servicos.categoria_servico import CategoriaServico
from src.servicos.registo_servico import RegistoServico
from src.servicos.venda_servico import VendaServico
from tests.falsos import RegistoFalso

ANA = Utilizador("Ana", "ana", bcrypt.hashpw(b"segredo", bcrypt.gensalt(rounds=4)).decode(), 2, "Funcionario",
                 id_utilizador=7)


class RegistosGuardados:
    """Faz de conta que é o repositório do registo de ações."""

    def __init__(self):
        self.registos = []

    def registar(self, registo):
        self.registos.append(registo)


class TestRegistoServico(unittest.TestCase):
    """O registo guarda quem fez cada ação (RF18)."""

    def setUp(self):
        self.repositorio = RegistosGuardados()
        self.servico = RegistoServico()
        self.servico.repositorio = self.repositorio

    def tearDown(self):
        sessao.terminar()

    def test_usa_o_utilizador_da_sessao(self):
        sessao.iniciar(ANA)
        self.servico.registar("CRIAR_CATEGORIA", "1 - Bebidas")
        self.assertEqual(self.repositorio.registos[0].id_utilizador, 7)

    def test_sem_sessao_fica_sem_utilizador(self):
        self.servico.registar("LOGIN_FALHADO", "username 'rui'")
        self.assertIsNone(self.repositorio.registos[0].id_utilizador)

    def test_detalhe_comprido_e_cortado_em_255(self):
        self.servico.registar("VENDA", "x" * 300, ANA)
        self.assertEqual(len(self.repositorio.registos[0].detalhe), 255)


class UtilizadoresFalsos:
    def __init__(self):
        ANA.tentativas_falhadas = 0
        self.utilizador = ANA

    def obter_por_username(self, username):
        return self.utilizador if username == "ana" else None

    def somar_tentativa_falhada(self, id_utilizador):
        self.utilizador.tentativas_falhadas += 1
        return self.utilizador.tentativas_falhadas

    def limpar_tentativas(self, id_utilizador):
        self.utilizador.tentativas_falhadas = 0


class TestAcoesRegistadas(unittest.TestCase):
    """Cada serviço regista as suas ações."""

    def setUp(self):
        self.registo = RegistoFalso()
        self.autenticacao = AutenticacaoServico()
        self.autenticacao.repositorio = UtilizadoresFalsos()
        self.autenticacao.registo = self.registo

    def tearDown(self):
        sessao.terminar()
        ANA.tentativas_falhadas = 0

    def test_login_e_logout(self):
        utilizador = self.autenticacao.iniciar_sessao("ana", "segredo")
        self.assertIs(sessao.utilizador_atual(), utilizador)
        self.autenticacao.terminar_sessao(utilizador)
        self.assertEqual(self.registo.acoes, ["LOGIN", "LOGOUT"])
        self.assertIsNone(sessao.utilizador_atual())

    def test_login_falhado_com_username_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.autenticacao.iniciar_sessao("rui", "segredo")
        self.assertEqual(self.registo.acoes, ["LOGIN_FALHADO"])

    def test_quinta_tentativa_regista_o_bloqueio(self):
        ANA.tentativas_falhadas = 4
        with self.assertRaises(ValueError):
            self.autenticacao.iniciar_sessao("ana", "errada")
        self.assertEqual(self.registo.acoes, ["LOGIN_FALHADO", "CONTA_BLOQUEADA"])

    def test_criar_categoria_e_registado(self):
        class Categorias:
            def criar(self, categoria):
                categoria.id_categoria = 1
                return categoria

        servico = CategoriaServico()
        servico.repositorio = Categorias()
        servico.registo = self.registo
        servico.criar("Bebidas")
        self.assertEqual(self.registo.acoes, ["CRIAR_CATEGORIA"])

    def test_venda_e_registada_e_venda_recusada_nao(self):
        class Produtos:
            def obter_por_codigo(self, codigo):
                return Produto("CAFE", "Café", Decimal("1.00"), 1, stock_atual=3, id_produto=2)

        class Vendas:
            def registar(self, venda):
                venda.id_venda = 1
                return venda

        servico = VendaServico()
        servico.repositorio, servico.produtos, servico.registo = Vendas(), Produtos(), self.registo
        carrinho = []
        servico.adicionar_linha(carrinho, "CAFE", "5")
        with self.assertRaises(ValueError):
            servico.registar(carrinho, ANA)
        self.assertEqual(self.registo.acoes, [])
        carrinho[0].quantidade = 2
        servico.registar(carrinho, ANA)
        self.assertEqual(self.registo.acoes, ["VENDA"])


if __name__ == "__main__":
    unittest.main()
