class LinhaVenda:
    """Um produto dentro de uma venda. Guarda o preço do momento da venda (RNF07)."""

    def __init__(self, id_produto, quantidade, preco_unitario, codigo=None, nome=None):
        self.id_produto = id_produto
        self.quantidade = quantidade
        self.preco_unitario = preco_unitario
        self.codigo = codigo
        self.nome = nome

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario


class Venda:
    """Uma venda ao balcão, com uma ou mais linhas (RF11)."""

    def __init__(self, id_utilizador, linhas=None, total=0, id_venda=None, data_venda=None,
                 username=None, numero_linhas=None):
        self.id_venda = id_venda
        self.data_venda = data_venda
        self.id_utilizador = id_utilizador
        self.linhas = linhas or []
        self.total = total
        self.username = username
        self.numero_linhas = numero_linhas
