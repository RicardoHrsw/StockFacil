from decimal import Decimal, InvalidOperation

from psycopg.errors import ForeignKeyViolation, UniqueViolation

from src.modelos.produto import Produto
from src.repositorios.produto_repositorio import ProdutoRepositorio

TAMANHO_MAXIMO_CODIGO = 30
TAMANHO_MAXIMO_NOME = 100
TAMANHO_MAXIMO_DESCRICAO = 255
PRECO_MAXIMO = Decimal("99999999.99")


def converter_preco(texto):
    """Converte o preço escrito (ex: "1,20" ou "1.20") num Decimal válido."""
    texto = str(texto or "").strip().replace(",", ".")
    if texto == "":
        raise ValueError("O preço de venda é obrigatório.")
    try:
        preco = Decimal(texto)
    except InvalidOperation:
        raise ValueError("O preço tem de ser um número, por exemplo 1,20.")
    if not preco.is_finite():
        raise ValueError("O preço tem de ser um número, por exemplo 1,20.")
    if preco < 0:
        raise ValueError("O preço não pode ser negativo.")
    if preco > PRECO_MAXIMO:
        raise ValueError(f"O preço não pode ser maior que {PRECO_MAXIMO}.")
    if preco.as_tuple().exponent < -2:
        raise ValueError("O preço só pode ter 2 casas decimais.")
    return preco


def converter_stock_minimo(texto):
    """Converte o stock mínimo num número inteiro. Em branco fica 0."""
    texto = str(texto or "").strip()
    if texto == "":
        return 0
    try:
        stock_minimo = int(texto)
    except ValueError:
        raise ValueError("O stock mínimo tem de ser um número inteiro, por exemplo 5.")
    if stock_minimo < 0:
        raise ValueError("O stock mínimo não pode ser negativo.")
    return stock_minimo


def converter_id_categoria(valor):
    """Confirma que foi escolhida uma categoria (um número inteiro positivo)."""
    try:
        id_categoria = int(str(valor).strip())
    except ValueError:
        raise ValueError("Escolha uma categoria da lista, pelo número.")
    if id_categoria <= 0:
        raise ValueError("Escolha uma categoria da lista, pelo número.")
    return id_categoria


def validar_produto(codigo, nome, preco_venda, id_categoria, descricao=None, stock_minimo=None):
    """Limpa e valida os dados. Devolve um Produto pronto a gravar."""
    codigo = (codigo or "").strip()
    nome = (nome or "").strip()
    descricao = (descricao or "").strip()

    if codigo == "":
        raise ValueError("O código do produto não pode estar vazio.")
    if len(codigo) > TAMANHO_MAXIMO_CODIGO:
        raise ValueError(f"O código não pode ter mais de {TAMANHO_MAXIMO_CODIGO} caracteres.")
    if nome == "":
        raise ValueError("O nome do produto não pode estar vazio.")
    if len(nome) > TAMANHO_MAXIMO_NOME:
        raise ValueError(f"O nome não pode ter mais de {TAMANHO_MAXIMO_NOME} caracteres.")
    if len(descricao) > TAMANHO_MAXIMO_DESCRICAO:
        raise ValueError(f"A descrição não pode ter mais de {TAMANHO_MAXIMO_DESCRICAO} caracteres.")

    if descricao == "":
        descricao = None

    return Produto(
        codigo=codigo,
        nome=nome,
        descricao=descricao,
        preco_venda=converter_preco(preco_venda),
        stock_minimo=converter_stock_minimo(stock_minimo),
        id_categoria=converter_id_categoria(id_categoria),
    )


class ProdutoServico:
    """Regras de negócio dos produtos."""

    def __init__(self):
        self.repositorio = ProdutoRepositorio()

    def listar(self):
        """Devolve os produtos ativos, ordenados por nome."""
        return self.repositorio.listar()

    def criar(self, codigo, nome, preco_venda, id_categoria, descricao=None, stock_minimo=None):
        """Valida os dados e grava um produto novo, com stock 0."""
        produto = validar_produto(codigo, nome, preco_venda, id_categoria, descricao, stock_minimo)
        try:
            return self.repositorio.criar(produto)
        except UniqueViolation:
            raise ValueError(f"Já existe um produto com o código '{produto.codigo}'.")
        except ForeignKeyViolation:
            raise ValueError("A categoria escolhida não existe. Escolha uma da lista.")
