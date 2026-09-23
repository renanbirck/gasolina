from pathlib import Path
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from os import environ
import logging

## database.py: arquivo que trata da conexão ao BD com os dados das pesquisas.
## O modelo de dados, com as tabelas e relacionamentos, é descrito em model.py

logging.basicConfig(level=logging.INFO) # O nível de logging é INFO.


# Permitir que a variável de ambiente DB_PATH seja usada para definir onde o DB está salvo.
# Vai facilitar os testes posteriormente.
# O caminho padrão é relativo a este arquivo (e não ao diretório atual), para funcionar
# independente de onde a aplicação for iniciada.

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "pesquisas.db"
DB_URL = f"sqlite:///{environ.get('DB_PATH', DEFAULT_DB_PATH)}"

# Criar a conexão ao BD

logging.info(f"O caminho do BD é {DB_URL}.")

# NullPool: cada sessão abre sua própria conexão (barato no SQLite). Com o pool padrão
# (5 + 10 conexões), as rotas 'async' travavam o servidor a partir de ~15 requisições
# simultâneas: o event loop ficava bloqueado esperando uma conexão que só seria devolvida
# pelo próprio event loop.
engine = create_engine(
    DB_URL, connect_args={"check_same_thread": False}, poolclass=NullPool
)

@event.listens_for(engine, "connect")
def configura_sqlite(dbapi_connection, _):
    # O SQLite só aplica as chaves estrangeiras se isso for ativado em cada conexão.
    # O WAL permite leituras simultâneas enquanto uma escrita acontece.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Até aqui, é quase tudo igual à documentação.

def aplica_migracoes():
    """ Cria os índices que o BD de produção não tem (o create_all não altera tabelas
        que já existem). É idempotente, então pode rodar a cada inicialização. """
    with engine.begin() as conn:
        # Garante que não haja dois preços do mesmo posto na mesma pesquisa,
        # e serve de índice para buscar os preços de uma pesquisa.
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uix_pesquisa_posto "
                          "ON Precos(IdPesquisa, IdPosto)"))
        # Para o histórico de um posto.
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_precos_posto ON Precos(IdPosto)"))
