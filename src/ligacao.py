import os                       # para ler variáveis do sistema
import psycopg                  # a biblioteca que fala com o PostgreSQL
from dotenv import load_dotenv  # lê o ficheiro .env

load_dotenv()  # carrega os dados do .env


def obter_ligacao():
    """Devolve uma ligação à base de dados."""
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )