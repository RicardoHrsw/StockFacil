from src.ligacao import obter_ligacao
from src.modelos.venda import Venda


class StockInsuficiente(Exception):
    """Durante a gravação, um produto já não tinha stock suficiente. A venda é desfeita."""

    def __init__(self, linha):
        super().__init__(linha.nome)
        self.linha = linha


class VendaRepositorio:
    """Guarda e lê vendas da base de dados."""

    def registar(self, venda):
        """Grava a venda, as linhas e a descida do stock numa só transação (RNF06).
        Se faltar stock num produto, nada fica gravado."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO venda (total, id_utilizador) VALUES (%s, %s)
                       RETURNING id_venda, data_venda""",
                    (venda.total, venda.id_utilizador),
                )
                venda.id_venda, venda.data_venda = cursor.fetchone()

                for linha in venda.linhas:
                    cursor.execute(
                        """UPDATE produto SET stock_atual = stock_atual - %s
                           WHERE id_produto = %s AND ativo AND stock_atual >= %s""",
                        (linha.quantidade, linha.id_produto, linha.quantidade),
                    )
                    if cursor.rowcount == 0:
                        raise StockInsuficiente(linha)
                    cursor.execute(
                        """INSERT INTO linha_venda (id_venda, id_produto, quantidade, preco_unitario)
                           VALUES (%s, %s, %s, %s)""",
                        (venda.id_venda, linha.id_produto, linha.quantidade, linha.preco_unitario),
                    )
        return venda

    def listar(self, limite=20):
        """Devolve as últimas vendas, da mais recente para a mais antiga."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """SELECT v.id_venda, v.data_venda, v.total, v.id_utilizador, u.username,
                              (SELECT COUNT(*) FROM linha_venda l WHERE l.id_venda = v.id_venda)
                       FROM venda v
                       JOIN utilizador u ON u.id_utilizador = v.id_utilizador
                       ORDER BY v.data_venda DESC, v.id_venda DESC
                       LIMIT %s""",
                    (limite,),
                )
                linhas = cursor.fetchall()
        return [
            Venda(id_venda=l[0], data_venda=l[1], total=l[2], id_utilizador=l[3], username=l[4], numero_linhas=l[5])
            for l in linhas
        ]
