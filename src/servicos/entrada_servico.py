from psycopg.errors import ForeignKeyViolation

from src.modelos.entrada_stock import EntradaStock
from src.repositorios.entrada_repositorio import EntradaRepositorio
from src.repositorios.produto_repositorio import ProdutoRepositorio
from src.servicos.fornecedor_servico import converter_id_fornecedor
from src.servicos.produto_servico import converter_preco

QUANTIDADE_MAXIMA = 100000


def converter_quantidade(texto):
    """Converte a quantidade num número inteiro maior que 0."""
    texto = str(texto or "").strip()
    try:
        quantidade = int(texto)
    except ValueError:
        raise ValueError("A quantidade tem de ser um número inteiro, por exemplo 12.")
    if quantidade <= 0:
        raise ValueError("A quantidade tem de ser maior que 0.")
    if quantidade > QUANTIDADE_MAXIMA:
        raise ValueError(f"A quantidade não pode ser maior que {QUANTIDADE_MAXIMA}.")
    return quantidade


class EntradaServico:
    """Regras das entradas de stock (RF10)."""

    def __init__(self):
        self.repositorio = EntradaRepositorio()
        self.produtos = ProdutoRepositorio()

    def listar(self):
        """Devolve as últimas entradas de stock."""
        return self.repositorio.listar()

    def registar(self, codigo, id_fornecedor, quantidade, preco_custo, utilizador):
        """Valida os dados, grava a entrada e devolve (entrada, produto, novo stock).
        Se o fornecedor ficar em branco, usa o fornecedor do produto."""
        codigo = (codigo or "").strip()
        produto = self.produtos.obter_por_codigo(codigo) if codigo else None
        if produto is None:
            raise ValueError(f"Não existe nenhum produto ativo com o código '{codigo}'.")

        if str(id_fornecedor or "").strip() == "":
            if produto.id_fornecedor is None:
                raise ValueError("Este produto não tem fornecedor. Escolha um da lista.")
            id_fornecedor = produto.id_fornecedor
        id_fornecedor = converter_id_fornecedor(id_fornecedor)

        entrada = EntradaStock(
            id_produto=produto.id_produto,
            id_fornecedor=id_fornecedor,
            id_utilizador=utilizador.id_utilizador,
            quantidade=converter_quantidade(quantidade),
            preco_custo=converter_preco(preco_custo, "preço de custo"),
        )
        try:
            novo_stock = self.repositorio.registar(entrada)
        except ForeignKeyViolation:
            raise ValueError("O fornecedor escolhido não existe. Escolha um da lista.")
        if novo_stock is None:
            raise ValueError("Este produto já não existe ou foi desativado.")
        return entrada, produto, novo_stock
