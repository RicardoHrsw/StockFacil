from src.interface.menu_categorias import MenuCategorias
from src.interface.menu_produtos import MenuProdutos


class MenuPrincipal:
    """Primeiro menu do programa: escolhe a área a gerir."""

    def mostrar(self):
        """Mostra o menu"""
        while True:
            print()
            print("=== StockFácil ===")
            print("1 - Categorias")
            print("2 - Produtos")
            print("0 - Sair")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                MenuCategorias().mostrar()
            elif opcao == "2":
                MenuProdutos().mostrar()
            elif opcao == "0":
                print("Até breve!")
                break
            else:
                print("Opção inválida. Escolha 1, 2 ou 0.")
