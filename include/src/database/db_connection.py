import os
import pandas as pd
import numpy as np
import logging
import pyodbc

from dotenv import load_dotenv
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

class AzureDataBase:
    """Azure SQL Database Connection."""
    def __init__(self) -> None:
        load_dotenv()

        self.db_user = os.getenv('DB_USER')
        self.db_pass = os.getenv('DB_PASS')
        self.db_server = os.getenv('DB_SERVER')
        self.db_port = os.getenv('DB_PORT')
        self.db_name = os.getenv('DB_NAME')

        self.params = quote_plus(
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
            pool_size=3,
            max_overflow=2,
            pool_recycle=600,
            pool_timeout=60,
            echo=False,
            isolation_level='READ UNCOMMITTED'
        )

    def _create_table(self, df: pd.DataFrame, table_name: str, conn) -> None:
        """Cria tabela com todas as colunas como NVARCHAR(MAX) para evitar problemas de tipo."""
        cols_sql = ',\n'.join([f'[{col}] NVARCHAR(MAX)' for col in df.columns])
        conn.execute(text(f'CREATE TABLE bronze.{table_name} (\n{cols_sql}\n)'))
        conn.execute(text(f"EXEC sp_tableoption 'bronze.{table_name}', 'large value types out of row', 1"))

    def _create_schema(self, conn) -> None:
        """Cria o schema bronze para as tabelas se não existir."""
        conn.execute(text(f"IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'bronze') BEGIN EXEC('CREATE SCHEMA bronze'); END"))

    def insert_data(self, data: pd.DataFrame, table_name: str) -> None:
        logger.info('Iniciando Inserção de Dados...')

        with self.engine.begin() as conn:
            try:
                self._create_schema(conn)
                conn.execute(text(f'DROP TABLE IF EXISTS bronze.{table_name}'))
                self._create_table(data, table_name, conn)

                raw_conn = conn.connection.dbapi_connection
                cursor = raw_conn.cursor()
                cursor.fast_executemany = True

                cols = ', '.join([f'[{c}]' for c in data.columns])
                placeholders = ', '.join(['?' for _ in data.columns])
                sql = f'INSERT INTO bronze.{table_name} ({cols}) VALUES ({placeholders})'

                chunk_size = 5000
                total = len(data)

                for i in range(0, total, chunk_size):
                    chunk = data.iloc[i:i + chunk_size]
                    rows = []
                    for row in chunk.itertuples(index=False, name=None):
                        clean = []
                        for v in row:
                            try:
                                clean.append(None if pd.isna(v) else v)
                            except (TypeError, ValueError):
                                clean.append(v)
                        rows.append(clean)

                    cursor.executemany(sql, rows)
                    raw_conn.commit()
                    del rows
                    logger.info(f'Inseridos {min(i + chunk_size, total):,} / {total:,}')

                cursor.close()
                logger.info(f'{table_name} atualizada com sucesso.')

            except Exception as e:
                logger.error(f'Erro ao inserir Dados: {str(e)}')
                raise