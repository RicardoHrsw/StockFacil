import unittest

import bcrypt

from src.modelos.utilizador import Utilizador
from src.servicos.autenticacao_servico import AutenticacaoServico, gerar_hash, password_correta

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

    def obter_por_username(self, username):
        return self.utilizador if username == "ana" else None

    def somar_tentativa_falhada(self, id_utilizador):
        self.utilizador.tentativas_falhadas += 1
        return self.utilizador.tentativas_falhadas

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


if __name__ == "__main__":
    unittest.main()
