import logging
import pandas as pd

from include.src.data.bitrix_collector import BitrixCollector

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)

api = BitrixCollector()

data = api.extract_data('crm_deal_uf')
df = pd.DataFrame(data, dtype=str)
print(f'Colunas: {len(df.columns)}')
print(df.columns.tolist())
print(len)