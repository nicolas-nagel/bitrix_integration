import os
import requests
import pandas as pd
import logging

from dotenv import load_dotenv
from typing import List, Dict, Any
from datetime import datetime

from include.src.database.db_connection import AzureDataBase

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

        self.db = AzureDataBase()

        self.SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.RELATIVE_PATH = os.getenv('RELATIVE_PATH')
        self.SMART_PROCESS_ID = os.getenv('SMART_PROCESS_ID')

        self.URL = f'https://{self.SERVER_ADDRESS}/{self.RELATIVE_PATH}?token={self.SECRET_KEY}'
        self.tables: List[str] = ['crm_deal', 'crm_deal_stage_history', 'user', 'crm_company', 'crm_stages']
        self.data: Dict[str, Any] = {}

    def start(self) -> None:
        logger.info('Iniciando Pipeline de Dados...')

        start_time = datetime.now()
        try:
            data = self.get_data()
            data = self.transform_data()
            data = self.load_data(data)

            end_time = datetime.now()
            pipeline_time = (end_time - start_time).total_seconds()
            logger.info(f'Pipeline concluída em {pipeline_time:.2f}s')
        
        except Exception as e:
            logger.error(f'Erro ao executar a pipeline: {str(e)}')
            raise

    def get_data(self) -> Dict[str, Any]:
        """
        Pega os Dados dos endpoints específicos e retorna um Dicionário com os Dados.
        
        Returns:
            Dict(str, Any): Dicionário com o nome do endpoint e o conteúdo em JSON.
        """
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
        """
        Transforma os arquivos em DataFrame para salvar no Banco de Dados.
        
        Returns:
            Dict(str, pd.DataFrame): Dicionário com nome do arquivo e o conteúdo em DataFrame.
        """
        logger.info('Iniciando Transformação de Dados...')

        result = {}
        try:
            for name, data in self.data.items():
                df = pd.DataFrame(data)
                df.columns = df.iloc[0].str.lower()
                df = df.drop(index=df.index[0], axis=0)
                df['inserted_at'] = datetime.now()

                logger.info(f'Arquivo: {name} transformado com sucesso.')
                result[name] = df

            logger.info(f'{len(result)} arquivos transformados com sucesso.')
            return result

        except Exception as e:
            logger.error(f'Erro ao transformar dados: {str(e)}')
            raise

    def load_data(self, data: Dict[str, pd.DataFrame]) -> None:
        """
        Salva os Dados do DataFrame no Banco de Dados.
        
        Args:
            data (Dict[str, pd.DataFrame]): Dicionário com 'nome do arquivo': DataFrame.

        Returns:
            None: Mensagem de sucesso, se erro, mensagem de erro.
        """
        logger.info('Preparando arquivos para inserir no Banco de Dados.')

        if not data or data is None:
            logger.warning('Inserção de Dados Cancelada. Nenhum dado foi passado.')
            raise

        try:
            for name, df in data.items():
                table_name = f'raw_{name}'
                self.db.insert_data(df, table_name)
                logger.info(f'Inserindo {len(df):.2f} registros em: {name}')

            logger.info(f'{len(data)} tabelas atualizadas.')

        except Exception as e:
            logger.error(f'Erro ao inserir dados no Banco de Dados: {str(e)}')
            raise