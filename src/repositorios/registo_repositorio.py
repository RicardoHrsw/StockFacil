from src.ligacao import obter_ligacao
from src.modelos.registo_acao import RegistoAcao


class RegistoRepositorio:
    """Guarda e lê o registo de ações."""

    def registar(self, registo):
        """Guarda uma ação. A data e a hora são postas pela base de dados."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO registo_acao (id_utilizador, acao, detalhe) VALUES (%s, %s, %s)",
                    (registo.id_utilizador, registo.acao, registo.detalhe),
                )

    def listar(self, limite=30):
        """Devolve as últimas ações, da mais recente para a mais antiga."""
        with obter_ligacao() as ligacao:
            with ligacao.cursor() as cursor:
                cursor.execute(
                    """SELECT r.id_registo, r.data_hora, r.id_utilizador, u.username, r.acao, r.detalhe
                       FROM registo_acao r
                       LEFT JOIN utilizador u ON u.id_utilizador = r.id_utilizador
                       ORDER BY r.data_hora DESC, r.id_registo DESC
                       LIMIT %s""",
                    (limite,),
                )
                linhas = cursor.fetchall()
        return [
            RegistoAcao(id_registo=l[0], data_hora=l[1], id_utilizador=l[2], username=l[3], acao=l[4], detalhe=l[5])
            for l in linhas
        ]
