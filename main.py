from src.ligacao import obter_ligacao
from src.modelos.categoria import Categoria
from src.repositorios.categoria_repositorio import CategoriaRepositorio

with obter_ligacao() as ligacao:
    with ligacao.cursor() as cursor:
        cursor.execute("SELECT nome FROM perfil")
        for linha in cursor.fetchall():
            print(linha[0])

repositorio = CategoriaRepositorio()
nova = repositorio.criar(Categoria("Bebidas", "Águas, sumos e refrigerantes"))
print(nova)     