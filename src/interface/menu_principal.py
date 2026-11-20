from src.interface.menu_categorias import MenuCategorias
from src.interface.menu_fornecedores import MenuFornecedores
from src.interface.menu_produtos import MenuProdutos


class MenuPrincipal:
    """Menu depois do login: escolhe a área a gerir."""

    def __init__(self, utilizador):
        self.utilizador = utilizador

    def mostrar(self):
        """Mostra o menu até o utilizador terminar a sessão."""
        while True:
            print()
            print("=== StockFácil ===")
            print(f"Sessão: {self.utilizador}")
            print("1 - Categorias")
            print("2 - Produtos")
            print("3 - Fornecedores")
            print("0 - Terminar sessão")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                MenuCategorias().mostrar()
            elif opcao == "2":
                MenuProdutos().mostrar()
            elif opcao == "3":
                MenuFornecedores().mostrar()
            elif opcao == "0":
                break
            else:
                print("Opção inválida. Escolha 1, 2, 3 ou 0.")
