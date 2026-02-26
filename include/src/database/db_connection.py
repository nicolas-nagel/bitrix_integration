import os
import pandas as pd
import numpy as np
import logging
import pyodbc
import math

from dotenv import load_dotenv
from urllib.parse import quote_plus
from decimal import Decimal

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
        use_sparse = len(df.columns) > 100
    
        col_defs = []
        for i, col in enumerate(df.columns):
            max_len = df[col].dropna().str.len().max()
            max_len = int(max_len) if pd.notna(max_len) else 1

            if max_len > 4000:
                col_defs.append(f'[{col}] NVARCHAR(MAX)')
            elif i == 0 or not use_sparse:
                col_defs.append(f'[{col}] NVARCHAR(4000)')
            else:
                col_defs.append(f'[{col}] NVARCHAR(4000) SPARSE NULL')

        cols_sql = ',\n'.join(col_defs)
        conn.execute(text(f'CREATE TABLE {table_name} (\n{cols_sql}\n)'))
        
        if any('NVARCHAR(MAX)' in d for d in col_defs):
            conn.execute(text(f"EXEC sp_tableoption '{table_name}', 'large value types out of row', 1"))

    def insert_data(self, data: pd.DataFrame, table_name: str, incremental: bool = False) -> None:
        logger.info('Iniciando Inserção de Dados...')

        with self.engine.begin() as conn:
            try:
                if not incremental:
                    conn.execute(text(f'DROP TABLE IF EXISTS {table_name}'))
                    self._create_table(data, table_name, conn)
                else:
                    # Só insere se a tabela já existe
                    conn.execute(text(f'''
                        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table_name}')
                        BEGIN
                            {self._get_create_sql(data, table_name)}
                        END
                    '''))

                raw_conn = conn.connection.dbapi_connection
                cursor = raw_conn.cursor()
                cursor.fast_executemany = True

                cols = ', '.join([f'[{c}]' for c in data.columns])
                placeholders = ', '.join(['?' for _ in data.columns])

                if incremental:
                    # Upsert: atualiza se existe, insere se não existe
                    id_col = data.columns[0]
                    update_cols = ', '.join([f'target.[{c}] = source.[{c}]' for c in data.columns if c != id_col])
                    sql = f'''
                        MERGE {table_name} AS target
                        USING (VALUES ({placeholders})) AS source ({cols})
                        ON target.[{id_col}] = source.[{id_col}]
                        WHEN MATCHED THEN UPDATE SET {update_cols}
                        WHEN NOT MATCHED THEN INSERT ({cols}) VALUES ({placeholders});
                    '''
                else:
                    sql = f'INSERT INTO {table_name} ({cols}) VALUES ({placeholders})'

                chunk_size = min(50000, max(5000, len(data) // 100))
                rows = [[None if pd.isna(v) else v for v in row] for row in data.itertuples(index=False, name=None)]

                for i in range(0, len(rows), chunk_size):
                    cursor.executemany(sql, rows[i:i + chunk_size])
                    raw_conn.commit()
                    logger.info(f'Inseridos {min(i + chunk_size, len(rows)):,} / {len(rows):,}')

                cursor.close()
                logger.info(f'{table_name} atualizada com sucesso.')

            except Exception as e:
                logger.error(f'Erro ao inserir Dados: {str(e)}')
                raise