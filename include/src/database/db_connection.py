import os
import pandas as pd
import logging

from dotenv import load_dotenv
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text

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

        self.conn_string = f'mssql+pyodbc:///?odbc_connect={self.params}'
        self.engine = create_engine(
            self.conn_string,
            pool_pre_ping=True,
            pool_size=1,
            max_overflow=1,
            pool_recycle=600,
            pool_timeout=30,
            connect_args={
                'timeout': 60,
                'fast_executemany': True
            },
            echo=False,
            isolation_level='READ UNCOMMITTED'
        )

    def insert_data(self, data: pd.DataFrame, table_name: str, use_truncate: bool = True) -> None:
        logger.info('Iniciando Inserção de Dados...')

        if data.empty:
            raise ValueError('data não pode estar vazio ou ser None.')
        
        if table_name is None:
            raise ValueError('table_name não pode ser vazio ou None.')
        
        with self.engine.begin() as conn:
            try:
                conn.execute(text(f'DROP TABLE IF EXISTS {table_name}'))

                chunk_size = 5000
                optimal_chunksize = (len(data) + chunk_size - 1) // chunk_size
                data.to_sql(
                    name=table_name,
                    con=conn,
                    index=False,
                    if_exists='replace',
                    chunksize=chunk_size
                )

                logger.info(f'{table_name} atualizada com sucesso.')

            except Exception as e:
                logger.error(f'Erro ao inserir Dados: {str(e)}')
                raise