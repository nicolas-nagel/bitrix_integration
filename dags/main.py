from pendulum import datetime
from airflow.sdk import dag, task

from include.src.data.bitrix_collector import BitrixCollector

@dag(
    dag_id='Bitrix_Pipeline',
    description='Pipeline de Dados das Tabelas do Bitrix para SQL Server',
    schedule='0 7,12,17,22 * * *',
    start_date=datetime(2026, 1, 29),
    catchup=False,
    max_active_runs=1,
    tags=['bitrix', 'sql-server', 'elt']
)
def pipeline():

    @task
    def task_pipeline():
        controller = BitrixCollector()
        return controller.start()
    
    t1 = task_pipeline()

    t1

pipeline()