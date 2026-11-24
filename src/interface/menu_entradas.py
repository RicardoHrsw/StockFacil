from src.interface.menu_produtos import MenuProdutos, formatar_preco
from src.ligacao import ErroLigacao
from src.servicos.entrada_servico import EntradaServico
from src.servicos.fornecedor_servico import FornecedorServico


class MenuEntradas:
    """Menu de consola para registar a mercadoria que chega à loja."""

    def __init__(self, sessao):
        self.sessao = sessao
        self.servico = EntradaServico()
        self.fornecedores = FornecedorServico()

    def mostrar(self):
        """Mostra o menu"""
        while True:
            print()
            print("=== StockFácil — Entradas de stock ===")
            print("1 - Registar entrada")
            print("2 - Ver últimas entradas")
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
        """Mostra os produtos, pede os dados da entrada e mostra o stock novo."""
        if not MenuProdutos().listar():
            return
        fornecedores = self.fornecedores.listar()
        if not fornecedores:
            print("Ainda não existem fornecedores. Registe primeiro um fornecedor.")
            return

        codigo = input("Código do produto: ")
        print()
        print("Fornecedores:")
        for fornecedor in fornecedores:
            print(str(fornecedor.id_fornecedor).rjust(4), "-", fornecedor.nome)
        id_fornecedor = input("Número do fornecedor (Enter para o fornecedor do produto): ")
        quantidade = input("Quantidade que chegou: ")
        preco_custo = input("Preço de custo por unidade (ex: 0,35): ")

        try:
            entrada, produto, novo_stock = self.servico.registar(codigo, id_fornecedor, quantidade, preco_custo,
                                                                 self.sessao)
            print(f"Entrada registada: +{entrada.quantidade} de '{produto.nome}'. "
                  f"Stock: {produto.stock_atual} → {novo_stock}.")
        except ValueError as erro:
            print("Erro:", erro)

    def listar(self):
        """Mostra as últimas entradas numa tabela."""
        entradas = self.servico.listar()
        if not entradas:
            print("Ainda não existem entradas de stock.")
            return

        largura_produto = max(len("Produto"), max(len(e.nome_produto) for e in entradas))
        largura_fornecedor = max(len("Fornecedor"), max(len(e.nome_fornecedor) for e in entradas))

        print()
        print("Data".ljust(16), "|", "Produto".ljust(largura_produto), "|", "Qtd".rjust(5), "|",
              "Custo".rjust(10), "|", "Fornecedor".ljust(largura_fornecedor), "|", "Por")
        print("-" * (largura_produto + largura_fornecedor + 55))
        for e in entradas:
            print(e.data_entrada.strftime("%d/%m/%Y %H:%M"), "|", e.nome_produto.ljust(largura_produto), "|",
                  str(e.quantidade).rjust(5), "|", formatar_preco(e.preco_custo).rjust(10), "|",
                  e.nome_fornecedor.ljust(largura_fornecedor), "|", e.username)
        print()
        print(f"Últimas {len(entradas)} entrada(s)")
