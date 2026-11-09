# StockFácil

Aplicação para gerir o stock e as vendas de pequenas lojas, feita em **Python** com **PostgreSQL**.

Projeto final da UFCD 5425 (Opção B, projeto livre).

O código está organizado em camadas:

| Camada | Pasta | O que faz |
|---|---|---|
| Interface | `src/interface/` | Menus na consola |
| Serviço | `src/servicos/` | Validações e regras |
| Repositório | `src/repositorios/` | SQL que guarda e lê da base de dados |
| Modelo | `src/modelos/` | As classes (ex: `Categoria`) |

**Estado atual:** registar e listar categorias.

---

## Requisitos

- Python 3.12 ou mais recente (testado com o 3.14)
- PostgreSQL (testado com o 18)

## Instalação

### 1. Descarregar o projeto

```
git clone https://github.com/RicardoHrsw/StockFacil.git
cd StockFacil
```

### 2. Criar o ambiente virtual e instalar as bibliotecas

Windows (PowerShell):

```
py -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux / macOS:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Criar a base de dados

Cria uma base de dados nova e vazia e corre o script `base_dados/stockfacil.sql` lá dentro. O script cria as tabelas e os perfis (Administrador e Funcionario).

Com o `psql`:

```
createdb -U postgres stockfacil
psql -U postgres -d stockfacil -f base_dados/stockfacil.sql
```

> No Windows, se o comando não for encontrado, usa o caminho completo, por exemplo
> `"C:\Program Files\PostgreSQL\18\bin\psql.exe"`.

Com o pgAdmin: botão direito em *Databases* → *Create* → *Database* com o nome `stockfacil`. Depois abre a *Query Tool* nessa base de dados, abre o ficheiro `base_dados/stockfacil.sql` e carrega em *Execute*.

O script só se corre **uma vez**, numa base de dados nova. A aplicação nunca o corre sozinha.

### 4. Configurar a ligação

Copia o `.env.example` para `.env` e preenche com os teus dados:

```
copy .env.example .env      (Windows)
cp .env.example .env        (Linux / macOS)
```

O `.env` tem a palavra-passe da base de dados, por isso está no `.gitignore` e nunca vai para o GitHub.

## Executar

Com o ambiente virtual ativo, na pasta do projeto:

```
python main.py
```

Se aparecer *"Não foi possível ligar à base de dados"*, confirma que o serviço do PostgreSQL está ligado e que os dados do `.env` estão certos.
