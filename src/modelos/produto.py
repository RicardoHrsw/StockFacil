class Produto:
    """Um artigo à venda na loja (ex: Água 1,5 L, Caderno A4)."""

    def __init__(self, codigo, nome, preco_venda, id_categoria, descricao=None,
                 stock_minimo=0, stock_atual=0, ativo=True, id_fornecedor=None,
                 id_produto=None, nome_categoria=None):
        self.id_produto = id_produto
        self.codigo = codigo
        self.nome = nome
        self.descricao = descricao
        self.preco_venda = preco_venda
        self.stock_atual = stock_atual
        self.stock_minimo = stock_minimo
        self.ativo = ativo
        self.id_categoria = id_categoria
        self.id_fornecedor = id_fornecedor
        self.nome_categoria = nome_categoria

    def __str__(self):
        return f"{self.codigo} - {self.nome} ({self.preco_venda} €)"
