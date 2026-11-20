from src.ligacao import obter_ligacao
from src.modelos.produto import Produto

COLUNAS = """p.id_produto, p.codigo, p.nome, p.descricao, p.preco_venda,
             p.stock_atual, p.stock_minimo, p.ativo, p.id_categoria,
             p.id_fornecedor, c.nome"""


def linha_para_produto(linha):
    """Transforma uma linha do SELECT num objeto Produto."""
    return Produto(
        id_produto=linha[0], codigo=linha[1], nome=linha[2], descricao=linha[3],
        preco_venda=linha[4], stock_atual=linha[5], stock_minimo=linha[6], ativo=linha[7],
        id_categoria=linha[8], id_fornecedor=linha[9], nome_categoria=linha[10],
    )


class ProdutoRepositorio:
    """Guarda e lê produtos da base de dados."""

    def criar(self, produto):
        """Guarda um produto novo e devolve-o já com o id."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO produto
                           (codigo, nome, descricao, preco_venda, stock_minimo, id_categoria, id_fornecedor)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)
                       RETURNING id_produto""",
                    (produto.codigo, produto.nome, produto.descricao, produto.preco_venda,
                     produto.stock_minimo, produto.id_categoria, produto.id_fornecedor),
                )
                produto.id_produto = cursor.fetchone()[0]
        return produto

    def listar(self):
        """Devolve os produtos ativos, ordenados por nome, com o nome da categoria."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    f"""SELECT {COLUNAS}
                        FROM produto p
                        JOIN categoria c ON c.id_categoria = p.id_categoria
                        WHERE p.ativo
                        ORDER BY p.nome"""
                )
                linhas = cursor.fetchall()
        return [linha_para_produto(linha) for linha in linhas]

    def obter_por_codigo(self, codigo):
        """Devolve o produto ativo com este código, ou None se não existir."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    f"""SELECT {COLUNAS}
                        FROM produto p
                        JOIN categoria c ON c.id_categoria = p.id_categoria
                        WHERE p.codigo = %s AND p.ativo""",
                    (codigo,),
                )
                linha = cursor.fetchone()
        if linha is None:
            return None
        return linha_para_produto(linha)

    def editar(self, produto):
        """Atualiza os dados de um produto ativo. O stock não muda aqui.
        Devolve False se o produto não existir ou estiver desativado."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """UPDATE produto
                       SET codigo = %s, nome = %s, descricao = %s, preco_venda = %s,
                           stock_minimo = %s, id_categoria = %s
                       WHERE id_produto = %s AND ativo""",
                    (produto.codigo, produto.nome, produto.descricao, produto.preco_venda,
                     produto.stock_minimo, produto.id_categoria, produto.id_produto),
                )
                return cursor.rowcount > 0

    def desativar(self, id_produto):
        """Desativa o produto em vez de o apagar, para guardar o histórico.
        Devolve False se o produto não existir ou já estiver desativado."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    "UPDATE produto SET ativo = FALSE WHERE id_produto = %s AND ativo",
                    (id_produto,),
                )
                return cursor.rowcount > 0
