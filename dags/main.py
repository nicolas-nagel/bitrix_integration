from pendulum import datetime
from airflow.sdk import dag, task

from include.src.data.bitrix_collector import BitrixCollector

@dag(
    dag_id='Pipeline_Bitrix',
    description='Pipeline de Dados das Tabelas do Bitrix para SQL Server',
    schedule='0 7,12,17,22 * * *',
    start_date=datetime(2026, 1, 28),
    catchup=False
)
def pipeline():

    @task
    def task_extract_data():
        collector = BitrixCollector()
        return collector.get_data()
        

    @task
    def task_transform_data(data):
        collector = BitrixCollector()
        return collector.transform_data()

    @task
    def task_load_crm_deal(data):
        if 'crm_deal' in data:
            BitrixCollector().db.insert_data(data['crm_deal'], 'raw_crm_deal')

    @task
    def task_load_crm_stage(data):
        if 'crm_deal_stage_history' in data:
            BitrixCollector().db.insert_data(data['crm_deal_stage_history'], 'raw_crm_deal_stage_history')

    @task
    def task_load_crm_user(data):
        if 'user' in data:
            BitrixCollector().db.insert_data(data['user'], 'raw_user')

    extracted = task_extract_data()
    transformed = task_transform_data(extracted)
    [
        task_load_crm_deal(transformed),
        task_load_crm_stage(transformed),
        task_load_crm_user(transformed)
    ]

pipeline()