from src.interface.menu_principal import MenuPrincipal
from src.interface.palavra_passe import alterar_password, pedir_password
from src.ligacao import ErroLigacao
from src.servicos.autenticacao_servico import AutenticacaoServico, precisa_mudar_password


class MenuLogin:
    """Primeiro ecrã do programa: só entra quem tiver username e palavra-passe certos."""

    def __init__(self):
        self.servico = AutenticacaoServico()

    def mostrar(self):
        """Pede o login até o utilizador escolher sair. Depois do logout volta aqui."""
        while True:
            print()
            print("=== StockFácil — Iniciar sessão ===")
            username = input("Username (Enter para sair): ").strip()
            if username == "":
                print("Até breve!")
                break
            password = pedir_password("Palavra-passe: ")

            try:
                utilizador = self.servico.iniciar_sessao(username, password)
            except (ValueError, ErroLigacao) as erro:
                print("Erro:", erro)
                continue

            if precisa_mudar_password(password):
                print("Está a usar a palavra-passe inicial. Tem de a alterar antes de continuar.")
                if not alterar_password(self.servico, utilizador, atual=password):
                    self.terminar_sessao(utilizador)
                    print("A sessão não foi iniciada. Tente outra vez.")
                    continue

            print(f"Bem-vindo, {utilizador.nome}!")
            MenuPrincipal(utilizador, self.servico).mostrar()
            self.terminar_sessao(utilizador)
            print("Sessão terminada.")

    def terminar_sessao(self, utilizador):
        """Regista o logout. Se a base de dados estiver desligada, avisa mas não fecha o programa."""
        try:
            self.servico.terminar_sessao(utilizador)
        except ErroLigacao as erro:
            print("Erro:", erro)
