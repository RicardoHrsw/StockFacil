-- postgre

CREATE TABLE perfil (
    id_perfil SERIAL PRIMARY KEY,
    nome VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE utilizador (
    id_utilizador SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    id_perfil INTEGER NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    tentativas_falhadas INTEGER NOT NULL DEFAULT 0,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_perfil) REFERENCES perfil (id_perfil)
);

CREATE TABLE categoria (
    id_categoria SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    descricao VARCHAR(255)
);

CREATE TABLE fornecedor (
    id_fornecedor SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    nif VARCHAR(9) UNIQUE,
    telefone VARCHAR(20),
    email VARCHAR(100),
    morada VARCHAR(255)
);

CREATE TABLE produto (
    id_produto SERIAL PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    descricao VARCHAR(255),
    preco_venda NUMERIC(10,2) NOT NULL CHECK (preco_venda >= 0),
    stock_atual INTEGER NOT NULL DEFAULT 0 CHECK (stock_atual >= 0),
    stock_minimo INTEGER NOT NULL DEFAULT 0 CHECK (stock_minimo >= 0),
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    id_categoria INTEGER NOT NULL,
    id_fornecedor INTEGER,
    FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria),
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedor (id_fornecedor)
);

CREATE TABLE venda (
    id_venda SERIAL PRIMARY KEY,
    data_venda TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total NUMERIC(10,2) NOT NULL DEFAULT 0 CHECK (total >= 0),
    id_utilizador INTEGER NOT NULL,
    FOREIGN KEY (id_utilizador) REFERENCES utilizador (id_utilizador)
);

CREATE TABLE linha_venda (
    id_linha SERIAL PRIMARY KEY,
    id_venda INTEGER NOT NULL,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10,2) NOT NULL CHECK (preco_unitario >= 0),
    FOREIGN KEY (id_venda) REFERENCES venda (id_venda) ON DELETE CASCADE,
    FOREIGN KEY (id_produto) REFERENCES produto (id_produto)
);

CREATE TABLE entrada_stock (
    id_entrada SERIAL PRIMARY KEY,
    data_entrada TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_produto INTEGER NOT NULL,
    id_fornecedor INTEGER NOT NULL,
    id_utilizador INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_custo NUMERIC(10,2) NOT NULL CHECK (preco_custo >= 0),
    FOREIGN KEY (id_produto) REFERENCES produto (id_produto),
    FOREIGN KEY (id_fornecedor) REFERENCES fornecedor (id_fornecedor),
    FOREIGN KEY (id_utilizador) REFERENCES utilizador (id_utilizador)
);

CREATE TABLE registo_acao (
    id_registo SERIAL PRIMARY KEY,
    data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_utilizador INTEGER,
    acao VARCHAR(50) NOT NULL,
    detalhe VARCHAR(255),
    FOREIGN KEY (id_utilizador) REFERENCES utilizador (id_utilizador)
);

INSERT INTO perfil (nome) VALUES ('Administrador'), ('Funcionario');
