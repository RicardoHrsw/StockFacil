from src.ligacao import ErroLigacao
from src.servicos.fornecedor_servico import FornecedorServico


def pedir_opcional(rotulo, atual):
    """Pede um campo opcional ao editar: Enter mantém, '-' apaga."""
    resposta = input(f"{rotulo} [{atual or '-'}] (escreva - para apagar): ").strip()
    if resposta == "":
        return atual or ""
    if resposta == "-":
        return ""
    return resposta


class MenuFornecedores:
    """Menu de consola para gerir fornecedores."""

    def __init__(self):
        self.servico = FornecedorServico()

    def mostrar(self):
        """Mostra o menu"""
        while True:
            print()
            print("=== StockFácil — Fornecedores ===")
            print("1 - Registar fornecedor")
            print("2 - Listar fornecedores")
            print("3 - Editar fornecedor")
            print("4 - Apagar fornecedor")
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
                    self.apagar()
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida. Escolha 1, 2, 3, 4 ou 0.")
            except ErroLigacao as erro:
                print("Erro:", erro)

    def registar(self):
        """Pede os dados ao utilizador e regista o fornecedor."""
        print("Só o nome é obrigatório. Enter deixa o campo vazio.")
        nome = input("Nome: ")
        nif = input("NIF (9 dígitos): ")
        telefone = input("Telefone: ")
        email = input("Email: ")
        morada = input("Morada: ")
        try:
            fornecedor = self.servico.criar(nome, nif, telefone, email, morada)
            print(f"Fornecedor '{fornecedor.nome}' registado com o número {fornecedor.id_fornecedor}.")
        except ValueError as erro:
            print("Erro:", erro)

    def editar(self):
        """Mostra a lista, pede o número do fornecedor e os dados novos."""
        if not self.listar():
            return
        try:
            fornecedor = self.servico.obter(input("Número do fornecedor a editar: "))
            print("Enter mantém o valor atual.")
            nome = input(f"Nome [{fornecedor.nome}]: ").strip() or fornecedor.nome
            nif = pedir_opcional("NIF", fornecedor.nif)
            telefone = pedir_opcional("Telefone", fornecedor.telefone)
            email = pedir_opcional("Email", fornecedor.email)
            morada = pedir_opcional("Morada", fornecedor.morada)
            fornecedor = self.servico.editar(fornecedor.id_fornecedor, nome, nif, telefone, email, morada)
            print(f"Fornecedor {fornecedor.id_fornecedor} atualizado: {fornecedor.nome}.")
        except ValueError as erro:
            print("Erro:", erro)

    def apagar(self):
        """Mostra a lista, pede o número do fornecedor e confirma antes de apagar."""
        if not self.listar():
            return
        try:
            fornecedor = self.servico.obter(input("Número do fornecedor a apagar: "))
            resposta = input(f"Tem a certeza que quer apagar '{fornecedor.nome}'? (s/n): ").strip().lower()
            if resposta != "s":
                print("Nada foi apagado.")
                return
            self.servico.apagar(fornecedor.id_fornecedor)
            print(f"Fornecedor '{fornecedor.nome}' apagado.")
        except ValueError as erro:
            print("Erro:", erro)

    def listar(self):
        """Mostra todos os fornecedores numa tabela. Devolve False se não houver nenhum."""
        fornecedores = self.servico.listar()

        if not fornecedores:
            print("Ainda não existem fornecedores registados.")
            return False

        largura_nome = max(len("Nome"), max(len(f.nome) for f in fornecedores))
        largura_telefone = max(len("Telefone"), max(len(f.telefone or "-") for f in fornecedores))

        print()
        print("ID".rjust(4), "|", "Nome".ljust(largura_nome), "|", "NIF".ljust(9), "|",
              "Telefone".ljust(largura_telefone), "|", "Email")
        print("-" * (largura_nome + largura_telefone + 45))
        for f in fornecedores:
            print(str(f.id_fornecedor).rjust(4), "|", f.nome.ljust(largura_nome), "|", (f.nif or "-").ljust(9), "|",
                  (f.telefone or "-").ljust(largura_telefone), "|", f.email or "-")
        print()
        print(f"Total: {len(fornecedores)} fornecedor(es)")
        return True
