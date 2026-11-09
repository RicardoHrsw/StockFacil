import os                       # para ler variáveis do sistema
import psycopg                  # a biblioteca que fala com o PostgreSQL
from dotenv import load_dotenv  # lê o ficheiro .env

load_dotenv()  # carrega os dados do .env

TEMPO_MAXIMO_LIGACAO = 5


class ErroLigacao(Exception):
    """A base de dados não está disponível (desligada, dados do .env errados, etc.)."""


def obter_ligacao():
    """Devolve uma ligação à base de dados."""
    try:
        return psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            connect_timeout=TEMPO_MAXIMO_LIGACAO,
        )
    except psycopg.OperationalError:
        raise ErroLigacao(
            "Não foi possível ligar à base de dados. "
            "Confirma que o PostgreSQL está ligado e que o ficheiro .env está correto."
        )
