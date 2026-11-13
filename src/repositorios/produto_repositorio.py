from src.ligacao import obter_ligacao
from src.modelos.produto import Produto


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
                    """SELECT p.id_produto, p.codigo, p.nome, p.descricao, p.preco_venda,
                              p.stock_atual, p.stock_minimo, p.ativo, p.id_categoria,
                              p.id_fornecedor, c.nome
                       FROM produto p
                       JOIN categoria c ON c.id_categoria = p.id_categoria
                       WHERE p.ativo
                       ORDER BY p.nome"""
                )
                linhas = cursor.fetchall()

        produtos = []
        for linha in linhas:
            produtos.append(Produto(
                id_produto=linha[0], codigo=linha[1], nome=linha[2], descricao=linha[3],
                preco_venda=linha[4], stock_atual=linha[5], stock_minimo=linha[6], ativo=linha[7],
                id_categoria=linha[8], id_fornecedor=linha[9], nome_categoria=linha[10],
            ))
        return produtos
