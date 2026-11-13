import unittest

from psycopg.errors import UniqueViolation

from src.servicos.categoria_servico import CategoriaServico, validar_categoria


class TestValidarCategoria(unittest.TestCase):
    """Testes às validações da categoria. Não usam a base de dados."""

    def test_nome_valido(self):
        nome, descricao = validar_categoria("Bebidas", "Águas e sumos")
        self.assertEqual(nome, "Bebidas")
        self.assertEqual(descricao, "Águas e sumos")

    def test_tira_espacos_do_inicio_e_do_fim(self):
        nome, descricao = validar_categoria("  Bebidas  ", "  Águas  ")
        self.assertEqual(nome, "Bebidas")
        self.assertEqual(descricao, "Águas")

    def test_nome_vazio_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_categoria("", None)

    def test_nome_so_com_espacos_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_categoria("     ", None)

    def test_nome_none_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_categoria(None, None)

    def test_nome_com_50_caracteres_e_aceite(self):
        nome, _ = validar_categoria("a" * 50, None)
        self.assertEqual(len(nome), 50)

    def test_nome_com_51_caracteres_e_recusado(self):
        with self.assertRaises(ValueError):
            validar_categoria("a" * 51, None)

    def test_descricao_com_255_caracteres_e_aceite(self):
        _, descricao = validar_categoria("Bebidas", "a" * 255)
        self.assertEqual(len(descricao), 255)

    def test_descricao_com_256_caracteres_e_recusada(self):
        with self.assertRaises(ValueError):
            validar_categoria("Bebidas", "a" * 256)

    def test_descricao_vazia_fica_none(self):
        _, descricao = validar_categoria("Bebidas", "")
        self.assertIsNone(descricao)

    def test_descricao_so_com_espacos_fica_none(self):
        _, descricao = validar_categoria("Bebidas", "   ")
        self.assertIsNone(descricao)

    def test_descricao_none_fica_none(self):
        _, descricao = validar_categoria("Bebidas", None)
        self.assertIsNone(descricao)


class RepositorioFalso:
    """Faz de conta que é o repositório, para testar o serviço sem base de dados."""

    def __init__(self, nome_repetido=False):
        self.nome_repetido = nome_repetido
        self.gravadas = []

    def criar(self, categoria):
        if self.nome_repetido:
            raise UniqueViolation()
        categoria.id_categoria = 1
        self.gravadas.append(categoria)
        return categoria


class TestCategoriaServico(unittest.TestCase):
    """Testes ao serviço com um repositório falso."""

    def criar_servico(self, repositorio):
        servico = CategoriaServico()
        servico.repositorio = repositorio
        return servico

    def test_categoria_valida_e_gravada(self):
        repositorio = RepositorioFalso()
        servico = self.criar_servico(repositorio)
        categoria = servico.criar("  Bebidas  ", "")
        self.assertEqual(categoria.nome, "Bebidas")
        self.assertIsNone(categoria.descricao)
        self.assertEqual(len(repositorio.gravadas), 1)

    def test_categoria_invalida_nao_e_gravada(self):
        repositorio = RepositorioFalso()
        servico = self.criar_servico(repositorio)
        with self.assertRaises(ValueError):
            servico.criar("   ", None)
        self.assertEqual(len(repositorio.gravadas), 0)

    def test_nome_repetido_da_mensagem_clara(self):
        servico = self.criar_servico(RepositorioFalso(nome_repetido=True))
        with self.assertRaises(ValueError) as contexto:
            servico.criar("Bebidas", None)
        self.assertIn("Já existe", str(contexto.exception))


if __name__ == "__main__":
    unittest.main()
