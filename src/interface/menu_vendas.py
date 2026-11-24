from src.interface.menu_produtos import MenuProdutos, formatar_preco
from src.ligacao import ErroLigacao
from src.servicos.venda_servico import VendaServico


class MenuVendas:
    """Menu de consola para registar vendas ao balcão."""

    def __init__(self, sessao):
        self.sessao = sessao
        self.servico = VendaServico()

    def mostrar(self):
        """Mostra o menu"""
        while True:
            print()
            print("=== StockFácil — Vendas ===")
            print("1 - Registar venda")
            print("2 - Ver últimas vendas")
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
        """Pede os produtos um a um, mostra o resumo e grava a venda depois de confirmar."""
        if not MenuProdutos().listar():
            return

        carrinho = []
        print("Escreva o código e a quantidade de cada produto. Enter no código termina.")
        while True:
            codigo = input("Código do produto (Enter para terminar): ").strip()
            if codigo == "":
                break
            quantidade = input("Quantidade: ")
            try:
                linha = self.servico.adicionar_linha(carrinho, codigo, quantidade)
                print(f"  No carrinho: {linha.quantidade} x {linha.nome} = {formatar_preco(linha.subtotal)}")
            except ValueError as erro:
                print("Erro:", erro)

        if not carrinho:
            print("Venda cancelada: não tem produtos.")
            return

        self.mostrar_carrinho(carrinho)
        resposta = input("Confirmar a venda? (s/n): ").strip().lower()
        if resposta != "s":
            print("Venda cancelada. Nada foi gravado.")
            return

        try:
            venda = self.servico.registar(carrinho, self.sessao)
            print(f"Venda n.º {venda.id_venda} registada. Total: {formatar_preco(venda.total)}")
        except ValueError as erro:
            print("Erro:", erro)

    def mostrar_carrinho(self, carrinho):
        """Mostra as linhas da venda e o total."""
        largura_nome = max(len("Produto"), max(len(l.nome) for l in carrinho))
        print()
        print("Produto".ljust(largura_nome), "|", "Qtd".rjust(5), "|", "Preço".rjust(10), "|", "Subtotal".rjust(12))
        print("-" * (largura_nome + 38))
        for l in carrinho:
            print(l.nome.ljust(largura_nome), "|", str(l.quantidade).rjust(5), "|",
                  formatar_preco(l.preco_unitario).rjust(10), "|", formatar_preco(l.subtotal).rjust(12))
        print("-" * (largura_nome + 38))
        total = sum(l.subtotal for l in carrinho)
        print("TOTAL".ljust(largura_nome + 23), "|", formatar_preco(total).rjust(12))

    def listar(self):
        """Mostra as últimas vendas numa tabela."""
        vendas = self.servico.listar()
        if not vendas:
            print("Ainda não existem vendas.")
            return

        print()
        print("N.º".rjust(5), "|", "Data".ljust(16), "|", "Linhas".rjust(6), "|", "Total".rjust(12), "|", "Por")
        print("-" * 60)
        for v in vendas:
            print(str(v.id_venda).rjust(5), "|", v.data_venda.strftime("%d/%m/%Y %H:%M"), "|",
                  str(v.numero_linhas).rjust(6), "|", formatar_preco(v.total).rjust(12), "|", v.username)
        print()
        print(f"Últimas {len(vendas)} venda(s)")
