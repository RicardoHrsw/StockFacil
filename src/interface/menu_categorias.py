from src.servicos.categoria_servico import CategoriaServico


class MenuCategorias:
    """Menu de consola para gerir categorias."""

    def __init__(self):
        self.servico = CategoriaServico()

    def mostrar(self):
        """Mostra o menu até o utilizador escolher sair."""
        while True:
            print()
            print("=== StockFácil — Categorias ===")
            print("1 - Registar categoria")
            print("2 - Listar categorias")
            print("0 - Sair")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                self.registar()
            elif opcao == "2":
                self.listar()
            elif opcao == "0":
                print("Até breve!")
                break
            else:
                print("Opção inválida. Escolha 1, 2 ou 0.")

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
        """Mostra todas as categorias."""
        for categoria in self.servico.listar():
            print(categoria)
