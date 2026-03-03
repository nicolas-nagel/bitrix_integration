import os
import requests
import pandas as pd
import logging

from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from requests.exceptions import HTTPError

from include.src.database.db_connection import AzureDataBase

logger = logging.getLogger(__name__)

load_dotenv()

class BitrixCollector:
    """Responsável por fazer a Coleta de Dados da API do Bitrix."""

    def __init__(self) -> None:

        self.db_conn = AzureDataBase()
        
        self.server_adress = os.getenv('SERVER_ADDRESS')
        self.relative_path = os.getenv('RELATIVE_PATH')
        self.secret_key = os.getenv('SECRET_KEY')
        self.smart_process = os.getenv('SMART_PROCESS_ID')
        self.url = f'https://{self.server_adress}/{self.relative_path}'

    def extract_data(self, table_name: str) -> pd.DataFrame:
        logger.info('Iniciando Coleta de Dados...')
        
        if not table_name or table_name is None:
            logger.error('Coleta cancelada, nenhuma tabela foi passada.')
            raise ValueError('table_name não pode estar vazio ou ser None.')

        try:
            params = {
                'token': self.secret_key,
                'table': table_name
            }

            response = requests.get(self.url, params=params)
            response.raise_for_status()

            result = response.json()
            headers = [data.lower() for data in result[0]]
            rows = result[1:]

            return pd.DataFrame(rows, columns=headers, dtype=str)
        
        except HTTPError as e:
            logger.error(f'Erro ao coletar dados da API: {str(e)}')
            raise

    def transform_data(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        logger.info('Iniciando Transformação de Dados...')

        UF_FIELDS = {
                'crm_deal_uf': [
                    'uf_crm_1761327651',
                    'uf_crm_1674504869',
                    'uf_crm_1758224216498',
                    'uf_crm_1672781757',
                    'uf_crm_1672781723',
                    'uf_crm_1673994278222',
                    'uf_crm_63c14d3c80814'
                ],
                'crm_dynamic_items_162': [
                    'xml_id',
                    'title',
                    'created_time',
                    'closedate',
                    'opportunity',
                    'category_id'
                ]
            }
        
        BR_TZ = timezone(timedelta(hours=-3))
        try:
            df['inserted_at'] = datetime.now(BR_TZ).strftime('%Y-%m-%d %H:%M:%S')

            if table_name in UF_FIELDS:
                id_col = df.columns[0]
                fields = UF_FIELDS[table_name]
                cols_to_keep = [id_col] + [f for f in fields if f in df.columns] + ['inserted_at']
                df = df[cols_to_keep]

            return df

        except Exception as e:
            logger.error(f'Erro ao transformar arquivo: {str(e)}')
            raise

    def load_data(self, data: pd.DataFrame, table_name: str) -> None:
        logger.info('Preparando Dados para Inserção no Banco...')

        if data is None or data.empty:
            logger.warning('Operação Cancelada, nenhum dado foi passado.')
            raise ValueError('data não pode estar vazio ou ser None.')
        
        try:
            logger.info(f'{len(data):,} linhas a serem inseridas.')
            self.db_conn.insert_data(data, table_name)

        except Exception as e:
            logger.error(f'Erro ao preparar Dados: {str(e)}')
            raise