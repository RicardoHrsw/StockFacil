from src.interface.palavra_passe import pedir_password
from src.ligacao import ErroLigacao
from src.servicos.utilizador_servico import UtilizadorServico


class MenuUtilizadores:
    """Menu de consola para o Administrador gerir os utilizadores."""

    def __init__(self, sessao):
        self.sessao = sessao
        self.servico = UtilizadorServico()

    def mostrar(self):
        """Mostra o menu"""
        while True:
            print()
            print("=== StockFácil — Utilizadores ===")
            print("1 - Registar utilizador")
            print("2 - Listar utilizadores")
            print("3 - Editar utilizador")
            print("4 - Desativar utilizador")
            print("5 - Desbloquear conta")
            print("0 - Voltar")
            opcao = input("Escolha uma opção: ").strip()

            try:
                if opcao == "1":
                    self.registar()
                elif opcao == "2":
                    self.listar()
                elif opcao == "3":
                    self.editar()
                elif opcao == "4":
                    self.desativar()
                elif opcao == "5":
                    self.desbloquear()
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida. Escolha 1, 2, 3, 4, 5 ou 0.")
            except ErroLigacao as erro:
                print("Erro:", erro)

    def mostrar_perfis(self):
        """Mostra os perfis para escolher pelo número."""
        print()
        print("Perfis:")
        for id_perfil, nome in self.servico.listar_perfis():
            print(str(id_perfil).rjust(4), "-", nome)

    def registar(self):
        """Pede os dados e a palavra-passe inicial, que o Administrador combina com a pessoa."""
        nome = input("Nome: ")
        username = input("Username (sem espaços): ")
        self.mostrar_perfis()
        id_perfil = input("Número do perfil: ")
        password = pedir_password("Palavra-passe inicial (mínimo 6 caracteres): ")
        confirmacao = pedir_password("Repita a palavra-passe: ")
        try:
            utilizador = self.servico.criar(nome, username, id_perfil, password, confirmacao)
            print(f"Utilizador '{utilizador.username}' registado como {utilizador.nome_perfil}.")
        except ValueError as erro:
            print("Erro:", erro)

    def editar(self):
        """Mostra a lista, pede o número do utilizador e os dados novos."""
        if not self.listar():
            return
        try:
            utilizador = self.servico.obter(input("Número do utilizador a editar: "))
            print("Enter mantém o valor atual.")
            nome = input(f"Nome [{utilizador.nome}]: ").strip() or utilizador.nome
            username = input(f"Username [{utilizador.username}]: ").strip() or utilizador.username
            self.mostrar_perfis()
            id_perfil = input(f"Número do perfil [{utilizador.id_perfil} - {utilizador.nome_perfil}]: ").strip() \
                or utilizador.id_perfil
            utilizador = self.servico.editar(utilizador.id_utilizador, nome, username, id_perfil, self.sessao)
            if utilizador.id_utilizador == self.sessao.id_utilizador:
                self.sessao.nome, self.sessao.username = utilizador.nome, utilizador.username
            print(f"Utilizador {utilizador.id_utilizador} atualizado: {utilizador.username} ({utilizador.nome_perfil}).")
        except ValueError as erro:
            print("Erro:", erro)

    def desativar(self):
        """Mostra a lista, pede o número do utilizador e confirma antes de desativar."""
        if not self.listar():
            return
        try:
            utilizador = self.servico.obter(input("Número do utilizador a desativar: "))
            resposta = input(f"Tem a certeza que quer desativar '{utilizador.username}'? (s/n): ").strip().lower()
            if resposta != "s":
                print("Nada foi alterado.")
                return
            self.servico.desativar(utilizador.id_utilizador, self.sessao)
            print(f"Utilizador '{utilizador.username}' desativado. Deixa de poder entrar, mas o histórico fica guardado.")
        except ValueError as erro:
            print("Erro:", erro)

    def desbloquear(self):
        """Mostra a lista e desbloqueia a conta escolhida."""
        if not self.listar():
            return
        try:
            utilizador = self.servico.desbloquear(input("Número do utilizador a desbloquear: "))
            print(f"A conta de '{utilizador.username}' foi desbloqueada.")
        except ValueError as erro:
            print("Erro:", erro)

    def listar(self):
        """Mostra todos os utilizadores numa tabela. Devolve False se não houver nenhum."""
        utilizadores = self.servico.listar()

        if not utilizadores:
            print("Ainda não existem utilizadores registados.")
            return False

        largura_username = max(len("Username"), max(len(u.username) for u in utilizadores))
        largura_nome = max(len("Nome"), max(len(u.nome) for u in utilizadores))

        print()
        print("ID".rjust(4), "|", "Username".ljust(largura_username), "|", "Nome".ljust(largura_nome), "|",
              "Perfil".ljust(13), "|", "Estado")
        print("-" * (largura_username + largura_nome + 40))
        for u in utilizadores:
            print(str(u.id_utilizador).rjust(4), "|", u.username.ljust(largura_username), "|",
                  u.nome.ljust(largura_nome), "|", u.nome_perfil.ljust(13), "|", u.estado)
        print()
        print(f"Total: {len(utilizadores)} utilizador(es)")
        return True
