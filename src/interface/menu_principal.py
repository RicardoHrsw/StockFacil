from src.interface.menu_categorias import MenuCategorias
from src.interface.menu_fornecedores import MenuFornecedores
from src.interface.menu_produtos import MenuProdutos
from src.interface.palavra_passe import alterar_password


class MenuPrincipal:
    """Menu depois do login: escolhe a área a gerir."""

    def __init__(self, utilizador, autenticacao):
        self.utilizador = utilizador
        self.autenticacao = autenticacao

    def mostrar(self):
        """Mostra o menu até o utilizador terminar a sessão."""
        while True:
            print()
            print("=== StockFácil ===")
            print(f"Sessão: {self.utilizador}")
            print("1 - Categorias")
            print("2 - Produtos")
            print("3 - Fornecedores")
            print("4 - Alterar a minha palavra-passe")
            print("0 - Terminar sessão")
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                MenuCategorias().mostrar()
            elif opcao == "2":
                MenuProdutos().mostrar()
            elif opcao == "3":
                MenuFornecedores().mostrar()
            elif opcao == "4":
                alterar_password(self.autenticacao, self.utilizador)
            elif opcao == "0":
                break
            else:
                print("Opção inválida. Escolha 1, 2, 3, 4 ou 0.")
