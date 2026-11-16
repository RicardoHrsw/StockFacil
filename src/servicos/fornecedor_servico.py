from psycopg.errors import ForeignKeyViolation, UniqueViolation

from src.modelos.fornecedor import Fornecedor
from src.repositorios.fornecedor_repositorio import FornecedorRepositorio

TAMANHO_MAXIMO_NOME = 100
TAMANHO_MAXIMO_TELEFONE = 20
TAMANHO_MAXIMO_EMAIL = 100
TAMANHO_MAXIMO_MORADA = 255
CARACTERES_TELEFONE = set("0123456789 +")


def opcional(texto):
    """Tira os espaços; um campo em branco fica None."""
    texto = (texto or "").strip()
    return texto or None


def validar_fornecedor(nome, nif=None, telefone=None, email=None, morada=None):
    """Limpa e valida os dados. Devolve um Fornecedor pronto a gravar."""
    nome = (nome or "").strip()
    nif = opcional(nif)
    telefone = opcional(telefone)
    email = opcional(email)
    morada = opcional(morada)

    if nome == "":
        raise ValueError("O nome do fornecedor não pode estar vazio.")
    if len(nome) > TAMANHO_MAXIMO_NOME:
        raise ValueError(f"O nome não pode ter mais de {TAMANHO_MAXIMO_NOME} caracteres.")

    if nif is not None:
        nif = nif.replace(" ", "")
        if len(nif) != 9 or not nif.isdigit():
            raise ValueError("O NIF tem de ter exatamente 9 dígitos.")

    if telefone is not None:
        if len(telefone) > TAMANHO_MAXIMO_TELEFONE:
            raise ValueError(f"O telefone não pode ter mais de {TAMANHO_MAXIMO_TELEFONE} caracteres.")
        if not set(telefone) <= CARACTERES_TELEFONE:
            raise ValueError("O telefone só pode ter números, espaços e o sinal +.")

    if email is not None:
        if len(email) > TAMANHO_MAXIMO_EMAIL:
            raise ValueError(f"O email não pode ter mais de {TAMANHO_MAXIMO_EMAIL} caracteres.")
        utilizador, arroba, dominio = email.partition("@")
        if " " in email or not utilizador or not arroba or "." not in dominio:
            raise ValueError("O email não é válido. Exemplo: geral@empresa.pt")

    if morada is not None and len(morada) > TAMANHO_MAXIMO_MORADA:
        raise ValueError(f"A morada não pode ter mais de {TAMANHO_MAXIMO_MORADA} caracteres.")

    return Fornecedor(nome, nif, telefone, email, morada)


def converter_id_fornecedor(valor):
    """Confirma que o número do fornecedor é um inteiro positivo."""
    try:
        id_fornecedor = int(str(valor).strip())
    except ValueError:
        raise ValueError("Escolha um fornecedor da lista, pelo número.")
    if id_fornecedor <= 0:
        raise ValueError("Escolha um fornecedor da lista, pelo número.")
    return id_fornecedor


class FornecedorServico:
    """Regras de negócio dos fornecedores."""

    def __init__(self):
        self.repositorio = FornecedorRepositorio()

    def listar(self):
        """Devolve todos os fornecedores, ordenados por nome."""
        return self.repositorio.listar()

    def obter(self, id_fornecedor):
        """Devolve o fornecedor com este número, ou dá erro se não existir."""
        id_fornecedor = converter_id_fornecedor(id_fornecedor)
        fornecedor = self.repositorio.obter(id_fornecedor)
        if fornecedor is None:
            raise ValueError(f"Não existe nenhum fornecedor com o número {id_fornecedor}.")
        return fornecedor

    def criar(self, nome, nif=None, telefone=None, email=None, morada=None):
        """Valida os dados e grava um fornecedor novo."""
        fornecedor = validar_fornecedor(nome, nif, telefone, email, morada)
        try:
            return self.repositorio.criar(fornecedor)
        except UniqueViolation:
            raise ValueError(f"Já existe um fornecedor com o NIF {fornecedor.nif}.")

    def editar(self, id_fornecedor, nome, nif=None, telefone=None, email=None, morada=None):
        """Valida os dados novos e atualiza o fornecedor."""
        fornecedor = validar_fornecedor(nome, nif, telefone, email, morada)
        fornecedor.id_fornecedor = converter_id_fornecedor(id_fornecedor)
        try:
            encontrado = self.repositorio.editar(fornecedor)
        except UniqueViolation:
            raise ValueError(f"Já existe um fornecedor com o NIF {fornecedor.nif}.")
        if not encontrado:
            raise ValueError(f"Não existe nenhum fornecedor com o número {fornecedor.id_fornecedor}.")
        return fornecedor

    def apagar(self, id_fornecedor):
        """Apaga o fornecedor, desde que não tenha produtos nem entradas de stock."""
        id_fornecedor = converter_id_fornecedor(id_fornecedor)
        try:
            encontrado = self.repositorio.apagar(id_fornecedor)
        except ForeignKeyViolation:
            raise ValueError("Não é possível apagar este fornecedor porque tem produtos ou entradas de stock associados.")
        if not encontrado:
            raise ValueError(f"Não existe nenhum fornecedor com o número {id_fornecedor}.")
