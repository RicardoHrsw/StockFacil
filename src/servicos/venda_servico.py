from src.modelos.venda import LinhaVenda, Venda
from src.repositorios.produto_repositorio import ProdutoRepositorio
from src.repositorios.venda_repositorio import StockInsuficiente, VendaRepositorio
from src.servicos.entrada_servico import converter_quantidade
from src.servicos.produto_servico import PRECO_MAXIMO


class VendaServico:
    """Regras das vendas (RF11, RF12 e RF13)."""

    def __init__(self):
        self.repositorio = VendaRepositorio()
        self.produtos = ProdutoRepositorio()

    def listar(self):
        """Devolve as últimas vendas."""
        return self.repositorio.listar()

    def adicionar_linha(self, carrinho, codigo, quantidade):
        """Junta um produto ao carrinho, com o preço de venda atual.
        Se o produto já estiver no carrinho, soma a quantidade. O stock só é verificado no fim."""
        codigo = (codigo or "").strip()
        produto = self.produtos.obter_por_codigo(codigo) if codigo else None
        if produto is None:
            raise ValueError(f"Não existe nenhum produto ativo com o código '{codigo}'.")
        quantidade = converter_quantidade(quantidade)

        for linha in carrinho:
            if linha.id_produto == produto.id_produto:
                linha.quantidade += quantidade
                return linha
        linha = LinhaVenda(produto.id_produto, quantidade, produto.preco_venda, produto.codigo, produto.nome)
        carrinho.append(linha)
        return linha

    def verificar_stock(self, carrinho):
        """Confirma o stock de todas as linhas. Se faltar num produto, a venda toda é recusada (RF13)."""
        faltas = []
        for linha in carrinho:
            produto = self.produtos.obter_por_codigo(linha.codigo)
            if produto is None:
                faltas.append(f"'{linha.nome}' já não está à venda")
            elif linha.quantidade > produto.stock_atual:
                faltas.append(f"'{linha.nome}': pediu {linha.quantidade}, só há {produto.stock_atual}")
        if faltas:
            raise ValueError("Não há stock suficiente. A venda não foi gravada.\n  " + "\n  ".join(faltas))

    def registar(self, carrinho, utilizador):
        """Grava a venda toda ou nada (RNF06). Devolve a venda com o número e o total."""
        if not carrinho:
            raise ValueError("A venda não tem produtos. Nada foi gravado.")
        self.verificar_stock(carrinho)

        total = sum(linha.subtotal for linha in carrinho)
        if total > PRECO_MAXIMO:
            raise ValueError(f"O total da venda não pode ser maior que {PRECO_MAXIMO}.")

        venda = Venda(utilizador.id_utilizador, carrinho, total)
        try:
            return self.repositorio.registar(venda)
        except StockInsuficiente as erro:
            raise ValueError(f"Não há stock suficiente de '{erro.linha.nome}'. A venda não foi gravada.")
