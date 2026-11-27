from decimal import Decimal, InvalidOperation

from psycopg.errors import ForeignKeyViolation, UniqueViolation

from src.modelos.produto import Produto
from src.repositorios.produto_repositorio import ProdutoRepositorio
from src.servicos.registo_servico import RegistoServico
from src.servicos.fornecedor_servico import converter_id_fornecedor

TAMANHO_MAXIMO_CODIGO = 30
TAMANHO_MAXIMO_NOME = 100
TAMANHO_MAXIMO_DESCRICAO = 255
PRECO_MAXIMO = Decimal("99999999.99")


def converter_preco(texto, rotulo="preço de venda"):
    """Converte o preço escrito (ex: "1,20" ou "1.20") num Decimal válido."""
    texto = str(texto or "").strip().replace(",", ".")
    if texto == "":
        raise ValueError(f"O {rotulo} é obrigatório.")
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


def converter_fornecedor_opcional(valor):
    """O fornecedor é opcional: em branco fica None, senão tem de ser um número válido."""
    if valor is None or str(valor).strip() == "":
        return None
    return converter_id_fornecedor(valor)


def mensagem_chave_estrangeira(erro):
    """Diz ao utilizador se foi a categoria ou o fornecedor que não existe."""
    restricao = getattr(erro.diag, "constraint_name", None) or ""
    if "fornecedor" in restricao:
        return "O fornecedor escolhido não existe. Escolha um da lista."
    return "A categoria escolhida não existe. Escolha uma da lista."


def validar_produto(codigo, nome, preco_venda, id_categoria, descricao=None, stock_minimo=None, id_fornecedor=None):
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
        id_fornecedor=converter_fornecedor_opcional(id_fornecedor),
    )


class ProdutoServico:
    """Regras de negócio dos produtos."""

    def __init__(self):
        self.repositorio = ProdutoRepositorio()
        self.registo = RegistoServico()

    def listar(self):
        """Devolve os produtos ativos, ordenados por nome."""
        return self.repositorio.listar()

    def listar_stock_baixo(self):
        """Devolve os produtos com stock igual ou abaixo do mínimo, os mais urgentes primeiro."""
        return self.repositorio.listar_stock_baixo()

    def criar(self, codigo, nome, preco_venda, id_categoria, descricao=None, stock_minimo=None, id_fornecedor=None):
        """Valida os dados e grava um produto novo, com stock 0."""
        produto = validar_produto(codigo, nome, preco_venda, id_categoria, descricao, stock_minimo, id_fornecedor)
        try:
            produto = self.repositorio.criar(produto)
        except UniqueViolation:
            raise ValueError(f"Já existe um produto com o código '{produto.codigo}'.")
        except ForeignKeyViolation as erro:
            raise ValueError(mensagem_chave_estrangeira(erro))
        self.registo.registar("CRIAR_PRODUTO", f"{produto.codigo} - {produto.nome}")
        return produto

    def obter(self, codigo):
        """Devolve o produto ativo com este código, ou dá erro se não existir."""
        codigo = (codigo or "").strip()
        if codigo == "":
            raise ValueError("Escreva o código do produto.")
        produto = self.repositorio.obter_por_codigo(codigo)
        if produto is None:
            raise ValueError(f"Não existe nenhum produto ativo com o código '{codigo}'.")
        return produto

    def editar(self, id_produto, codigo, nome, preco_venda, id_categoria, descricao=None, stock_minimo=None,
               id_fornecedor=None):
        """Valida os dados novos e atualiza o produto. O stock atual não muda."""
        produto = validar_produto(codigo, nome, preco_venda, id_categoria, descricao, stock_minimo, id_fornecedor)
        produto.id_produto = id_produto
        try:
            encontrado = self.repositorio.editar(produto)
        except UniqueViolation:
            raise ValueError(f"Já existe um produto com o código '{produto.codigo}'.")
        except ForeignKeyViolation as erro:
            raise ValueError(mensagem_chave_estrangeira(erro))
        if not encontrado:
            raise ValueError("Este produto já não existe ou foi desativado.")
        self.registo.registar("EDITAR_PRODUTO", f"{produto.codigo} - {produto.nome}")
        return produto

    def desativar(self, id_produto):
        """Desativa o produto: deixa de aparecer, mas o histórico de vendas fica guardado."""
        if not self.repositorio.desativar(id_produto):
            raise ValueError("Este produto já não existe ou já estava desativado.")
        self.registo.registar("DESATIVAR_PRODUTO", f"produto n.º {id_produto}")
