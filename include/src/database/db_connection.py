import os
import pandas as pd
import logging

from dotenv import load_dotenv
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from include.src.database.db_model import Base

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

class AzureDataBase:
    """Azure SQL Database Connection."""
    def __init__(self) -> None:
        load_dotenv()

        self.db_user = os.getenv('DB_USER')
        self.db_pass = os.getenv('DB_PASS')
        self.db_server = os.getenv('DB_SERVER')
        self.db_port = os.getenv('DB_PORT')
        self.db_name = os.getenv('DB_NAME')

        params = quote_plus(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.db_server};"
            f"DATABASE={self.db_name};"
            f"UID={self.db_user};"
            f"PWD={self.db_pass};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=120;"
            f"Login Timeout=120;"
            f"MultipleActiveResultSets=True;"
        )

        self.conn_string = f'mssql+pyodbc:///?odbc_connect={params}'
        self.engine = create_engine(
            self.conn_string, 
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=1800,
            pool_timeout=120,
            connect_args={'timeout': 120, 'connect_timeout': 120},
            echo=False,
        )


        self._Session = sessionmaker(bind=self.engine, autoflush=False)
        self.Base = Base

    def create_tables(self) -> None:
        """
        Cria as tabelas no Banco de Dados
        
        Returns:
            None: Tabelas no Banco de Dados criadas.
        """
        logger.info('Criando Tabelas no Banco de Dados...')

        try:
            self.Base.metadata.create_all(self.engine)
            logger.info('Tabelas Criadas com Sucesso.')

        except Exception as e:
            logger.error(f'Erro ao criar as tabelas: {str(e)}')
            raise

    def drop_tables(self) -> None:
        """
        Deleta as tabelas no Banco de Dados
        
        Returns:
            None: Tabelas no Banco de Dados deletadas.
        """
        logger.warning('Deletando TODAS as Tabelas do Banco de Dados...')

        try:
            self.Base.metadata.drop_all(self.engine)
            logger.info('Tabelas excluídas com sucesso.')

        except Exception as e:
            logger.error(f'Erro ao deletar as tabelas: {str(e)}')
            raise

    def insert_data(self, df: pd.DataFrame, table_name: str) -> None:
        """
        Insere os Dados no Banco de Dados.
        
        Args:
            df (pd.DataFrame): DataFrame com os Dados.
            table_name (str): Nome da tabela que será salvo no Banco.

        Returns:
            None: Mensagem de sucesso, se erro, mensagem de erro.
        """
        logger.info('Inserindo Dados no Banco...')

        try:
            num_cols = len(df.columns)
            chunk_size = max(500, min(15000, 2000 // num_cols))
            max_rows_multi = max(1, 2100 // num_cols)
            chunk_size = min(chunk_size, max_rows_multi)

            with self.engine.begin() as conn:

                try:
                    conn.execute(text(f'TRUNCATE TABLE {table_name}'))
                    if_exists_mode = 'append'
                except:
                    if_exists_mode = 'replace'

                df.to_sql(
                    name=table_name,
                    con=conn,
                    if_exists=if_exists_mode,
                    index=False,
                    chunksize=chunk_size,
                    method='multi'
                )
                logger.info(f'{len(df):.2f} dados inseridos em: {table_name}')

        except Exception as e:
            logger.error(f'Erro ao inserir dados no Banco: {str(e)}')
            raise