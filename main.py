from src.ligacao import obter_ligacao

with obter_ligacao() as ligacao:
    with ligacao.cursor() as cursor:
        cursor.execute("SELECT nome FROM perfil")
        for linha in cursor.fetchall():
            print(linha[0])