import os
import requests
import pandas as pd
import logging

from dotenv import load_dotenv
from typing import List, Dict, Any
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

    def extract_data(self, table_name: str) -> List[Dict[str, Any]]:
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

            data = [dict(zip(headers, row)) for row in rows]

            return data
        
        except HTTPError as e:
            logger.error(f'Erro ao coletar dados da API: {str(e)}')
            raise

    def transform_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        logger.info('Iniciando Transformação de Dados...')
        
        BR_TZ = timezone(timedelta(hours=-3))

        if not data or data is None:
            logger.warning('Transformação cancelada. Nenhum dado foi passado.')
            raise ValueError('data não pode estar vazio ou ser None.')
        
        try:
            df = pd.DataFrame(data)
            df['inserted_at'] = datetime.now(BR_TZ).replace(tzinfo=None, microsecond=0)

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