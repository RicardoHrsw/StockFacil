from src.ligacao import ErroLigacao
from src.servicos.categoria_servico import CategoriaServico
from src.servicos.produto_servico import ProdutoServico


def formatar_preco(preco):
    """Mostra o preço à portuguesa, ex: 1,20 €."""
    return f"{preco:.2f} €".replace(".", ",")


class MenuProdutos:
    """Menu de consola para gerir produtos."""

    def __init__(self):
        self.servico = ProdutoServico()
        self.categorias = CategoriaServico()

    def mostrar(self):
        """Mostra o menu"""
        while True:
            print()
            print("=== StockFácil — Produtos ===")
            print("1 - Registar produto")
            print("2 - Listar produtos")
            print("3 - Editar produto")
            print("4 - Desativar produto")
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
                elif opcao == "0":
                    break
                else:
                    print("Opção inválida. Escolha 1, 2, 3, 4 ou 0.")
            except ErroLigacao as erro:
                print("Erro:", erro)

    def registar(self):
        """Pede os dados ao utilizador e regista o produto numa categoria que já existe."""
        categorias = self.categorias.listar()
        if not categorias:
            print("Ainda não existem categorias. Registe primeiro uma categoria.")
            return

        codigo = input("Código: ")
        nome = input("Nome: ")
        descricao = input("Descrição (opcional, Enter para deixar vazio): ")
        preco = input("Preço de venda (ex: 1,20): ")
        stock_minimo = input("Stock mínimo (Enter para 0): ")

        self.mostrar_categorias(categorias)
        id_categoria = input("Número da categoria: ")

        try:
            produto = self.servico.criar(codigo, nome, preco, id_categoria, descricao, stock_minimo)
            print(f"Produto '{produto.nome}' registado com o código {produto.codigo}.")
        except ValueError as erro:
            print("Erro:", erro)

    def mostrar_categorias(self, categorias):
        """Mostra a lista de categorias para escolher pelo número."""
        print()
        print("Categorias:")
        for categoria in categorias:
            print(str(categoria.id_categoria).rjust(4), "-", categoria.nome)

    def editar(self):
        """Mostra a lista, pede o código do produto e os dados novos."""
        if not self.listar():
            return
        try:
            produto = self.servico.obter(input("Código do produto a editar: "))
            print("Enter mantém o valor atual.")
            codigo = input(f"Código [{produto.codigo}]: ").strip() or produto.codigo
            nome = input(f"Nome [{produto.nome}]: ").strip() or produto.nome
            descricao_atual = produto.descricao or ""
            descricao = input(f"Descrição [{descricao_atual or '-'}] (escreva - para apagar): ").strip()
            if descricao == "":
                descricao = descricao_atual
            elif descricao == "-":
                descricao = ""
            preco = input(f"Preço de venda [{formatar_preco(produto.preco_venda)}]: ").strip() or produto.preco_venda
            stock_minimo = input(f"Stock mínimo [{produto.stock_minimo}]: ").strip() or produto.stock_minimo
            self.mostrar_categorias(self.categorias.listar())
            id_categoria = input(f"Número da categoria [{produto.id_categoria} - {produto.nome_categoria}]: ").strip() or produto.id_categoria
            produto = self.servico.editar(produto.id_produto, codigo, nome, preco, id_categoria, descricao, stock_minimo)
            print(f"Produto {produto.codigo} atualizado: {produto.nome}.")
        except ValueError as erro:
            print("Erro:", erro)

    def desativar(self):
        """Mostra a lista, pede o código do produto e confirma antes de desativar."""
        if not self.listar():
            return
        try:
            produto = self.servico.obter(input("Código do produto a desativar: "))
            resposta = input(f"Tem a certeza que quer desativar '{produto.nome}'? (s/n): ").strip().lower()
            if resposta != "s":
                print("Nada foi alterado.")
                return
            self.servico.desativar(produto.id_produto)
            print(f"Produto '{produto.nome}' desativado. Deixa de aparecer na lista, mas o histórico fica guardado.")
        except ValueError as erro:
            print("Erro:", erro)

    def listar(self):
        """Mostra os produtos ativos numa tabela. Devolve False se não houver nenhum."""
        produtos = self.servico.listar()

        if not produtos:
            print("Ainda não existem produtos registados.")
            return False

        largura_codigo = max(len("Código"), max(len(p.codigo) for p in produtos))
        largura_nome = max(len("Nome"), max(len(p.nome) for p in produtos))
        largura_categoria = max(len("Categoria"), max(len(p.nome_categoria) for p in produtos))

        print()
        print("Código".ljust(largura_codigo), "|", "Nome".ljust(largura_nome), "|",
              "Categoria".ljust(largura_categoria), "|", "Preço".rjust(10), "|", "Stock", "|", "Mínimo")
        print("-" * (largura_codigo + largura_nome + largura_categoria + 40))
        for p in produtos:
            print(p.codigo.ljust(largura_codigo), "|", p.nome.ljust(largura_nome), "|",
                  p.nome_categoria.ljust(largura_categoria), "|", formatar_preco(p.preco_venda).rjust(10), "|",
                  str(p.stock_atual).rjust(5), "|", str(p.stock_minimo).rjust(6))
        print()
        print(f"Total: {len(produtos)} produto(s)")
        return True
