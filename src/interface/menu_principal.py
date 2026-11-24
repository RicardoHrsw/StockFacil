from src.interface.menu_categorias import MenuCategorias
from src.interface.menu_entradas import MenuEntradas
from src.interface.menu_fornecedores import MenuFornecedores
from src.interface.menu_produtos import MenuProdutos
from src.interface.menu_utilizadores import MenuUtilizadores
from src.interface.menu_vendas import MenuVendas
from src.interface.palavra_passe import alterar_password
from src.ligacao import ErroLigacao


class MenuPrincipal:
    """Menu depois do login. O Funcionário só vê as opções do seu perfil (RNF04)."""

    def __init__(self, utilizador, autenticacao):
        self.utilizador = utilizador
        self.autenticacao = autenticacao

    def opcoes(self):
        """Devolve as opções do menu, conforme o perfil, como pares (texto, função)."""
        if self.utilizador.e_administrador:
            return [
                ("Categorias", lambda: MenuCategorias().mostrar()),
                ("Produtos", lambda: MenuProdutos().mostrar()),
                ("Fornecedores", lambda: MenuFornecedores().mostrar()),
                ("Entradas de stock", lambda: MenuEntradas(self.utilizador).mostrar()),
                ("Vendas", lambda: MenuVendas(self.utilizador).mostrar()),
                ("Utilizadores", lambda: MenuUtilizadores(self.utilizador).mostrar()),
                ("Alterar a minha palavra-passe", self.alterar_password),
            ]
        return [
            ("Vendas", lambda: MenuVendas(self.utilizador).mostrar()),
            ("Entradas de stock", lambda: MenuEntradas(self.utilizador).mostrar()),
            ("Ver produtos", lambda: MenuProdutos().listar()),
            ("Alterar a minha palavra-passe", self.alterar_password),
        ]

    def alterar_password(self):
        alterar_password(self.autenticacao, self.utilizador)

    def mostrar(self):
        """Mostra o menu até o utilizador terminar a sessão."""
        while True:
            opcoes = self.opcoes()
            print()
            print("=== StockFácil ===")
            print(f"Sessão: {self.utilizador}")
            for numero, (texto, _) in enumerate(opcoes, start=1):
                print(f"{numero} - {texto}")
            print("0 - Terminar sessão")
            escolha = input("Escolha uma opção: ").strip()

            if escolha == "0":
                break
            if not escolha.isdecimal() or not 1 <= int(escolha) <= len(opcoes):
                print(f"Opção inválida. Escolha um número de 0 a {len(opcoes)}.")
                continue
            try:
                opcoes[int(escolha) - 1][1]()
            except ErroLigacao as erro:
                print("Erro:", erro)
