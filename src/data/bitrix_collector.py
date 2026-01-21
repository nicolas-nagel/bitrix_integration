import os
import requests
import pandas as pd
import json
import logging

from dotenv import load_dotenv
from typing import List, Dict, Optional, Any


load_dotenv()

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

class BitrixCollector:
    """Responsável por fazer a Coleta de Dados da API do Bitrix."""

    def __init__(self) -> None:

        load_dotenv()

        self.SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.RELATIVE_PATH = os.getenv('RELATIVE_PATH')
        self.SMART_PROCESS_ID = os.getenv('SMART_PROCESS_ID')

        self.URL = f'https://{self.SERVER_ADDRESS}/{self.RELATIVE_PATH}?token={self.SECRET_KEY}'
        self.tables: List[str] = ['crm_deal', 'crm_deal_stage_history']
        self.data: Dict[str, pd.DataFrame] = {}

    def start(self) -> None:
        ...

    def get_data(self) -> Dict[str, Any]:
        logger.info('Iniciando Coleta de Dados...')

        try:
            for table in self.tables:
                response = requests.get(url=f'{self.URL}&table={table}')
                if response.status_code == 200:
                    
                    result = response.json()
                    self.data[table] = result
                    logger.info(f'Endpoint: {table} Coletado com sucesso.')

            logger.info(f'{len(self.data)} arquivos coletados com sucesso.')
            return self.data
        
        except Exception as e:
            logger.error(f'Erro ao coletar os dados: {str(e)}')
            self.data = {}
            raise
                    
    def transform_data(self) -> Dict[str, pd.DataFrame]:
        logger.info('Iniciando Transformação de Dados...')

        result = {}
        try:
            for name, data in self.data.items():
                df = pd.DataFrame(data)
                df.columns = df.iloc[0].str.lower()
                df = df.drop(index=df.index[0], axis=0)

                logger.info(f'Arquivo: {name} transformado com sucesso.')
                result[name] = df

            logger.info(f'{len(result)} arquivos transformados com sucesso.')
            return result

        except Exception as e:
            logger.error(f'Erro ao transformar dados: {str(e)}')
            raise

    def load_data(self) -> None:
        ...