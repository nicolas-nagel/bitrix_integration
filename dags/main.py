import logging
import time

from typing import List
from datetime import datetime, timedelta

from airflow.sdk import dag, task

from include.src.data.bitrix_collector import BitrixCollector

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['nicolas.nagel@savecompany.com.br'],
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

@dag(
    dag_id='crm_bitrix_pipeline',
    default_args=default_args,
    description='ETL paralelo das Tabelas do Bitrix',
    schedule='0 */6 * * *',
    start_date=datetime(2026, 2, 24),
    catchup=False,
    tags=['bitrix', 'etl', 'azure'],
    max_active_runs=4
)
def bitrix_pipeline():

    @task
    def get_tables() -> List[str]:
        TABLES = ['crm_deal_stage_history', 'crm_deal_product_row', 'crm_deal', 'crm_dynamic_items_162', 'crm_company', 'crm_deal_uf', 'crm_product', 'crm_stages', 'user']

        return TABLES
    
    @task(
            retries=3,
            retry_delay=timedelta(seconds=30),
            pool='default_pool'
    )
    def insert_tables_data(table_name: str):
        task_start = time.time()

        try:
            full_table_name = f'raw_bitrix_{table_name}'
            api = BitrixCollector()

            extract_start = time.time()
            data = api.extract_data(table_name)
            extract_time = time.time() - extract_start

            transform_start = time.time()
            df = api.transform_data(data, table_name)
            transform_time = time.time() - transform_start

            load_start = time.time()
            api.load_data(df, full_table_name)
            load_time = time.time() - load_start

            total_time = time.time() - task_start

            
            logger.info(f'RESUMO: {full_table_name}')
            logger.info(f'-> Registros: {len(df):,}')
            logger.info(f'-> Extract:   {extract_time:6.1f}s')
            logger.info(f'-> Transform: {transform_time:6.1f}s')
            logger.info(f'-> Load:      {load_time:6.1f}s')
            logger.info(f'TOTAL:  {total_time:6.1f}s')

        except Exception as e:
            logger.error(f'Erro ao processar tabelas: {str(e)}')
            raise

        finally:
            if hasattr(api.db_conn, 'engine'):
                api.db_conn.engine.dispose()

    config = get_tables()
    insert_data = insert_tables_data.expand(table_name=config)

bitrix_pipeline()