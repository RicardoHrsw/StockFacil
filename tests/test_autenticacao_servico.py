import unittest

import bcrypt

from src.modelos.utilizador import Utilizador
from src.servicos.autenticacao_servico import (AutenticacaoServico, gerar_hash, password_correta,
                                              precisa_mudar_password, validar_nova_password)

HASH_SEGREDO = bcrypt.hashpw(b"segredo", bcrypt.gensalt(rounds=4)).decode()


class TestPassword(unittest.TestCase):
    """O hash da palavra-passe (RNF01)."""

    def test_hash_nao_guarda_a_password_em_texto(self):
        password_hash = gerar_hash("segredo")
        self.assertNotIn("segredo", password_hash)
        self.assertTrue(password_hash.startswith("$2b$"))

    def test_password_certa(self):
        self.assertTrue(password_correta("segredo", HASH_SEGREDO))

    def test_password_errada(self):
        self.assertFalse(password_correta("Segredo", HASH_SEGREDO))

    def test_password_longa_demais_e_errada_sem_rebentar(self):
        self.assertFalse(password_correta("x" * 100, HASH_SEGREDO))


class RepositorioFalso:
    """Faz de conta que é o repositório, com o utilizador 'ana' (palavra-passe 'segredo')."""

    def __init__(self, tentativas=0, ativo=True):
        self.utilizador = Utilizador("Ana", "ana", HASH_SEGREDO, 2, "Funcionario", ativo, tentativas, 1)
        self.limpezas = 0
        self.hashes_gravados = []

    def obter_por_username(self, username):
        return self.utilizador if username == "ana" else None

    def somar_tentativa_falhada(self, id_utilizador):
        self.utilizador.tentativas_falhadas += 1
        return self.utilizador.tentativas_falhadas

    def alterar_password(self, id_utilizador, password_hash):
        self.hashes_gravados.append(password_hash)
        return True

    def limpar_tentativas(self, id_utilizador):
        self.limpezas += 1
        self.utilizador.tentativas_falhadas = 0


class TestIniciarSessao(unittest.TestCase):
    """O login (RF01) e o bloqueio após 5 tentativas falhadas (RF02)."""

    def criar_servico(self, repositorio):
        servico = AutenticacaoServico()
        servico.repositorio = repositorio
        return servico

    def test_login_certo_devolve_o_utilizador(self):
        utilizador = self.criar_servico(RepositorioFalso()).iniciar_sessao("  ana ", "segredo")
        self.assertEqual(utilizador.nome, "Ana")

    def test_campos_vazios_sao_recusados(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso()).iniciar_sessao("", "")

    def test_username_que_nao_existe(self):
        with self.assertRaises(ValueError) as contexto:
            self.criar_servico(RepositorioFalso()).iniciar_sessao("rui", "segredo")
        self.assertIn("errados", str(contexto.exception))

    def test_password_errada_soma_uma_tentativa(self):
        repositorio = RepositorioFalso()
        with self.assertRaises(ValueError):
            self.criar_servico(repositorio).iniciar_sessao("ana", "errada")
        self.assertEqual(repositorio.utilizador.tentativas_falhadas, 1)

    def test_quinta_tentativa_errada_bloqueia(self):
        repositorio = RepositorioFalso(tentativas=4)
        with self.assertRaises(ValueError) as contexto:
            self.criar_servico(repositorio).iniciar_sessao("ana", "errada")
        self.assertIn("bloqueada", str(contexto.exception))
        self.assertTrue(repositorio.utilizador.bloqueado)

    def test_conta_bloqueada_recusa_mesmo_com_password_certa(self):
        with self.assertRaises(ValueError) as contexto:
            self.criar_servico(RepositorioFalso(tentativas=5)).iniciar_sessao("ana", "segredo")
        self.assertIn("bloqueada", str(contexto.exception))

    def test_login_certo_volta_a_por_o_contador_a_zero(self):
        repositorio = RepositorioFalso(tentativas=3)
        self.criar_servico(repositorio).iniciar_sessao("ana", "segredo")
        self.assertEqual(repositorio.utilizador.tentativas_falhadas, 0)
        self.assertEqual(repositorio.limpezas, 1)

    def test_utilizador_desativado_nao_entra(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso(ativo=False)).iniciar_sessao("ana", "segredo")


class TestNovaPassword(unittest.TestCase):
    """As regras da nova palavra-passe."""

    def test_password_valida(self):
        self.assertEqual(validar_nova_password("caixa2026", "caixa2026"), "caixa2026")

    def test_password_curta_e_recusada(self):
        with self.assertRaises(ValueError):
            validar_nova_password("abc12", "abc12")

    def test_password_longa_demais_e_recusada(self):
        with self.assertRaises(ValueError):
            validar_nova_password("x" * 73, "x" * 73)

    def test_confirmacao_diferente_e_recusada(self):
        with self.assertRaises(ValueError) as contexto:
            validar_nova_password("caixa2026", "caixa2025")
        self.assertIn("não são iguais", str(contexto.exception))

    def test_so_a_password_inicial_obriga_a_mudar(self):
        self.assertTrue(precisa_mudar_password("admin"))
        self.assertFalse(precisa_mudar_password("caixa2026"))


class TestAlterarPassword(unittest.TestCase):
    """Alterar a palavra-passe, indicando a atual (RF20)."""

    def setUp(self):
        self.repositorio = RepositorioFalso()
        self.servico = AutenticacaoServico()
        self.servico.repositorio = self.repositorio
        self.utilizador = self.repositorio.utilizador

    def test_alterar_com_a_password_atual_certa(self):
        self.servico.alterar_password(self.utilizador, "segredo", "caixa2026", "caixa2026")
        self.assertEqual(len(self.repositorio.hashes_gravados), 1)
        self.assertTrue(password_correta("caixa2026", self.utilizador.password_hash))

    def test_password_atual_errada_nao_muda_nada(self):
        with self.assertRaises(ValueError) as contexto:
            self.servico.alterar_password(self.utilizador, "errada", "caixa2026", "caixa2026")
        self.assertIn("atual está errada", str(contexto.exception))
        self.assertEqual(self.repositorio.hashes_gravados, [])

    def test_nova_igual_a_atual_e_recusada(self):
        with self.assertRaises(ValueError):
            self.servico.alterar_password(self.utilizador, "segredo", "segredo", "segredo")

    def test_nova_password_invalida_nao_muda_nada(self):
        with self.assertRaises(ValueError):
            self.servico.alterar_password(self.utilizador, "segredo", "abc", "abc")
        self.assertEqual(self.repositorio.hashes_gravados, [])


if __name__ == "__main__":
    unittest.main()
