import unittest

from psycopg.errors import UniqueViolation

from src.modelos.utilizador import Utilizador
from src.servicos.autenticacao_servico import password_correta
from src.servicos.utilizador_servico import UtilizadorServico, validar_dados
from tests.falsos import RegistoFalso


class TestValidarDados(unittest.TestCase):
    """Validações do nome e do username."""

    def test_tira_espacos(self):
        self.assertEqual(validar_dados("  Ana Silva ", " ana "), ("Ana Silva", "ana"))

    def test_nome_vazio_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_dados("  ", "ana")

    def test_username_vazio_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_dados("Ana", "")

    def test_username_com_espacos_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_dados("Ana", "ana silva")

    def test_username_com_51_caracteres_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_dados("Ana", "a" * 51)


class RepositorioFalso:
    """Faz de conta que é o repositório: 1 = admin, 2 = ana (bloqueada), 3 = rui (desativado)."""

    def __init__(self, erro=None):
        self.erro = erro
        self.utilizadores = {
            1: Utilizador("Administrador", "admin", "h", 1, "Administrador", id_utilizador=1),
            2: Utilizador("Ana", "ana", "h", 2, "Funcionario", tentativas_falhadas=5, id_utilizador=2),
            3: Utilizador("Rui", "rui", "h", 2, "Funcionario", ativo=False, id_utilizador=3),
        }
        self.gravados = []
        self.desativados = []
        self.desbloqueados = []

    def listar_perfis(self):
        return [(1, "Administrador"), (2, "Funcionario")]

    def obter(self, id_utilizador):
        return self.utilizadores.get(id_utilizador)

    def criar(self, utilizador):
        if self.erro:
            raise self.erro()
        utilizador.id_utilizador = 4
        self.gravados.append(utilizador)
        return utilizador

    def editar(self, utilizador):
        if self.erro:
            raise self.erro()
        return utilizador.ativo

    def desativar(self, id_utilizador):
        if not self.utilizadores[id_utilizador].ativo:
            return False
        self.desativados.append(id_utilizador)
        return True

    def limpar_tentativas(self, id_utilizador):
        self.desbloqueados.append(id_utilizador)


class TestUtilizadorServico(unittest.TestCase):
    """Gestão de utilizadores (RF04) e desbloqueio (RF05), sem base de dados."""

    def setUp(self):
        self.repositorio = RepositorioFalso()
        self.servico = UtilizadorServico()
        self.servico.repositorio = self.repositorio
        self.servico.registo = RegistoFalso()
        self.admin = self.repositorio.utilizadores[1]

    def test_criar_guarda_hash_e_nao_a_password(self):
        utilizador = self.servico.criar("Maria", "maria", "2", "caixa2026", "caixa2026")
        self.assertEqual(utilizador.nome_perfil, "Funcionario")
        self.assertNotEqual(utilizador.password_hash, "caixa2026")
        self.assertTrue(password_correta("caixa2026", utilizador.password_hash))

    def test_criar_com_perfil_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.servico.criar("Maria", "maria", "9", "caixa2026", "caixa2026")
        self.assertEqual(self.repositorio.gravados, [])

    def test_criar_com_password_curta(self):
        with self.assertRaises(ValueError):
            self.servico.criar("Maria", "maria", "2", "abc", "abc")

    def test_username_repetido_da_mensagem_clara(self):
        self.servico.repositorio = RepositorioFalso(erro=UniqueViolation)
        self.servico.registo = RegistoFalso()
        with self.assertRaises(ValueError) as contexto:
            self.servico.criar("Outra Ana", "ana", "2", "caixa2026", "caixa2026")
        self.assertIn("Já existe um utilizador com o username 'ana'", str(contexto.exception))

    def test_editar_muda_o_perfil(self):
        utilizador = self.servico.editar("2", "Ana", "ana", "1", self.admin)
        self.assertEqual(utilizador.nome_perfil, "Administrador")

    def test_admin_nao_pode_tirar_a_si_proprio_o_perfil(self):
        with self.assertRaises(ValueError):
            self.servico.editar("1", "Administrador", "admin", "2", self.admin)

    def test_editar_desativado_e_recusado(self):
        with self.assertRaises(ValueError):
            self.servico.editar("3", "Rui", "rui", "2", self.admin)

    def test_desativar_outro_utilizador(self):
        self.servico.desativar("2", self.admin)
        self.assertEqual(self.repositorio.desativados, [2])

    def test_admin_nao_pode_desativar_a_propria_conta(self):
        with self.assertRaises(ValueError):
            self.servico.desativar("1", self.admin)
        self.assertEqual(self.repositorio.desativados, [])

    def test_desativar_duas_vezes_da_erro(self):
        with self.assertRaises(ValueError):
            self.servico.desativar("3", self.admin)

    def test_desbloquear_conta_bloqueada(self):
        utilizador = self.servico.desbloquear("2")
        self.assertFalse(utilizador.bloqueado)
        self.assertEqual(self.repositorio.desbloqueados, [2])

    def test_desbloquear_conta_que_nao_esta_bloqueada(self):
        with self.assertRaises(ValueError):
            self.servico.desbloquear("1")

    def test_utilizador_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.servico.obter("99")

    def test_estado_para_a_listagem(self):
        estados = [u.estado for u in self.repositorio.utilizadores.values()]
        self.assertEqual(estados, ["Ativo", "Bloqueado", "Desativado"])


if __name__ == "__main__":
    unittest.main()
