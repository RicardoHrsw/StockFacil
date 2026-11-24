from src.ligacao import obter_ligacao
from src.modelos.entrada_stock import EntradaStock


class EntradaRepositorio:
    """Guarda e lê as entradas de stock da base de dados."""

    def registar(self, entrada):
        """Grava a entrada e soma a quantidade ao stock do produto, numa só transação.
        Devolve o novo stock, ou None se o produto não existir ou estiver desativado."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """UPDATE produto SET stock_atual = stock_atual + %s
                       WHERE id_produto = %s AND ativo
                       RETURNING stock_atual""",
                    (entrada.quantidade, entrada.id_produto),
                )
                linha = cursor.fetchone()
                if linha is None:
                    return None
                cursor.execute(
                    """INSERT INTO entrada_stock (id_produto, id_fornecedor, id_utilizador, quantidade, preco_custo)
                       VALUES (%s, %s, %s, %s, %s)
                       RETURNING id_entrada, data_entrada""",
                    (entrada.id_produto, entrada.id_fornecedor, entrada.id_utilizador,
                     entrada.quantidade, entrada.preco_custo),
                )
                entrada.id_entrada, entrada.data_entrada = cursor.fetchone()
        return linha[0]

    def listar(self, limite=20):
        """Devolve as últimas entradas, da mais recente para a mais antiga."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """SELECT e.id_entrada, e.data_entrada, e.id_produto, e.id_fornecedor, e.id_utilizador,
                              e.quantidade, e.preco_custo, p.codigo, p.nome, f.nome, u.username
                       FROM entrada_stock e
                       JOIN produto p ON p.id_produto = e.id_produto
                       JOIN fornecedor f ON f.id_fornecedor = e.id_fornecedor
                       JOIN utilizador u ON u.id_utilizador = e.id_utilizador
                       ORDER BY e.data_entrada DESC, e.id_entrada DESC
                       LIMIT %s""",
                    (limite,),
                )
                linhas = cursor.fetchall()
        return [
            EntradaStock(id_entrada=l[0], data_entrada=l[1], id_produto=l[2], id_fornecedor=l[3],
                         id_utilizador=l[4], quantidade=l[5], preco_custo=l[6], codigo_produto=l[7],
                         nome_produto=l[8], nome_fornecedor=l[9], username=l[10])
            for l in linhas
        ]
