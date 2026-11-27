import unittest

from psycopg.errors import ForeignKeyViolation, UniqueViolation

from src.modelos.fornecedor import Fornecedor
from src.servicos.fornecedor_servico import FornecedorServico, validar_fornecedor
from tests.falsos import RegistoFalso


class TestValidarFornecedor(unittest.TestCase):
    """Testes às validações do fornecedor. Não usam a base de dados."""

    def test_so_com_nome(self):
        fornecedor = validar_fornecedor("  Águas do Sul  ")
        self.assertEqual(fornecedor.nome, "Águas do Sul")
        self.assertIsNone(fornecedor.nif)
        self.assertIsNone(fornecedor.email)

    def test_todos_os_campos(self):
        fornecedor = validar_fornecedor("Papelaria Lda", "123 456 789", "+351 289 000 000", "geral@papel.pt", "Rua A, Faro")
        self.assertEqual(fornecedor.nif, "123456789")
        self.assertEqual(fornecedor.telefone, "+351 289 000 000")

    def test_campos_em_branco_ficam_none(self):
        fornecedor = validar_fornecedor("X", "  ", "", " ", "")
        self.assertIsNone(fornecedor.nif)
        self.assertIsNone(fornecedor.telefone)
        self.assertIsNone(fornecedor.morada)

    def test_nome_vazio_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("   ")

    def test_nome_com_101_caracteres_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("N" * 101)

    def test_nif_com_8_digitos_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("X", nif="12345678")

    def test_nif_com_10_digitos_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("X", nif="1234567890")

    def test_nif_com_letras_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("X", nif="12345678A")

    def test_telefone_com_letras_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("X", telefone="289 ABC")

    def test_telefone_longo_demais_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("X", telefone="1" * 21)

    def test_email_sem_arroba_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("X", email="geral.papel.pt")

    def test_email_sem_ponto_no_dominio_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("X", email="geral@papel")

    def test_email_com_espacos_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("X", email="ge ral@papel.pt")

    def test_morada_com_256_caracteres_e_recusada(self):
        with self.assertRaises(ValueError):
            validar_fornecedor("X", morada="m" * 256)


class RepositorioFalso:
    """Faz de conta que é o repositório, com o fornecedor 1 guardado."""

    def __init__(self, erro=None):
        self.erro = erro
        self.fornecedores = {1: Fornecedor("Águas do Sul", "123456789", id_fornecedor=1)}
        self.gravados = []
        self.apagados = []

    def criar(self, fornecedor):
        if self.erro:
            raise self.erro()
        fornecedor.id_fornecedor = 2
        self.gravados.append(fornecedor)
        return fornecedor

    def obter(self, id_fornecedor):
        return self.fornecedores.get(id_fornecedor)

    def editar(self, fornecedor):
        if self.erro:
            raise self.erro()
        return fornecedor.id_fornecedor in self.fornecedores

    def apagar(self, id_fornecedor):
        if self.erro:
            raise self.erro()
        if id_fornecedor not in self.fornecedores:
            return False
        self.apagados.append(id_fornecedor)
        return True


class TestFornecedorServico(unittest.TestCase):
    """Testes ao serviço com um repositório falso."""

    def criar_servico(self, repositorio):
        servico = FornecedorServico()
        servico.repositorio = repositorio
        servico.registo = RegistoFalso()
        return servico

    def test_fornecedor_valido_e_gravado(self):
        repositorio = RepositorioFalso()
        self.criar_servico(repositorio).criar("Papelaria Lda", "987654321")
        self.assertEqual(len(repositorio.gravados), 1)

    def test_fornecedor_invalido_nao_e_gravado(self):
        repositorio = RepositorioFalso()
        with self.assertRaises(ValueError):
            self.criar_servico(repositorio).criar("Papelaria Lda", "123")
        self.assertEqual(len(repositorio.gravados), 0)

    def test_nif_repetido_da_mensagem_clara(self):
        servico = self.criar_servico(RepositorioFalso(erro=UniqueViolation))
        with self.assertRaises(ValueError) as contexto:
            servico.criar("Outro", "123456789")
        self.assertIn("Já existe um fornecedor com o NIF", str(contexto.exception))

    def test_editar_fornecedor_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso()).editar("7", "Novo")

    def test_obter_fornecedor_que_nao_existe(self):
        with self.assertRaises(ValueError):
            self.criar_servico(RepositorioFalso()).obter("7")

    def test_apagar_fornecedor_sem_historico(self):
        repositorio = RepositorioFalso()
        self.criar_servico(repositorio).apagar("1")
        self.assertEqual(repositorio.apagados, [1])

    def test_apagar_fornecedor_com_produtos_da_mensagem_clara(self):
        servico = self.criar_servico(RepositorioFalso(erro=ForeignKeyViolation))
        with self.assertRaises(ValueError) as contexto:
            servico.apagar("1")
        self.assertIn("tem produtos ou entradas de stock", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
