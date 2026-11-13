from src.ligacao import ErroLigacao
from src.servicos.categoria_servico import CategoriaServico

class MenuCategorias:
    """Menu de consola para gerir categorias."""

    def __init__(self):
        self.servico = CategoriaServico()

    def mostrar(self):
        """Mostra o menu"""
        while True:
            print()
            print("=== StockFácil — Categorias ===")
            print("1 - Registar categoria")
            print("2 - Listar categorias")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    self.registar()
                elif opcao == "2":
                    self.listar()
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida. Escolha 1, 2 ou 0.")
            except ErroLigacao as erro:
                print("Erro:", erro)

    def registar(self):
        """Pede os dados ao utilizador e regista a categoria."""
        nome = input("Nome: ")
        descricao = input("Descrição (opcional, Enter para deixar vazio): ")
        try:
            categoria = self.servico.criar(nome, descricao)
            print(f"Categoria '{categoria.nome}' registada com o número {categoria.id_categoria}.")
        except ValueError as erro:
            print("Erro:", erro)

    def listar(self):
        """Mostra todas as categorias numa tabela."""
        categorias = self.servico.listar()

        if not categorias:
            print("Ainda não existem categorias registadas.")
            return

        largura_nome = max(len("Nome"), max(len(categoria.nome) for categoria in categorias))

        print()
        print("ID".rjust(4), "|", "Nome".ljust(largura_nome), "|", "Descrição")
        print("-" * (largura_nome + 30))
        for categoria in categorias:
            descricao = categoria.descricao or "-"
            print(str(categoria.id_categoria).rjust(4), "|", categoria.nome.ljust(largura_nome), "|", descricao)
        print()
        print(f"Total: {len(categorias)} categoria(s)")
