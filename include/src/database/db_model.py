from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class CRMDeal(Base):
    """Modelo da tabela 'raw_crm_deal' para o Banco de Dados."""

    __tablename__ = 'raw_crm_deal'

    id = Column(Integer, primary_key=True, unique=True, index=True)
    date_create = Column(DateTime, nullable=False)
    date_modify = Column(DateTime, nullable=False)
    created_by_id = Column(Integer, nullable=False)
    created_by_name = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    modify_by_id = Column(Integer, nullable=False)
    modified_by_name = Column(String, nullable=True)
    modified_by = Column(String, nullable=False)
    assigned_by_id = Column(Integer, nullable=False)
    assigned_by_name = Column(String, nullable=False)
    assigned_by = Column(String, nullable=False)
    assigned_by_department = Column(String, nullable=True)
    opened = Column(String, nullable=False)
    lead_id = Column(String, nullable=True)
    company_id = Column(Integer, nullable=True)
    company_name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    contact_id = Column(String, nullable=True)
    contact_name = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    title = Column(String, nullable=False)
    crm_product_id = Column(String, nullable=True)
    crm_product = Column(String, nullable=True)
    crm_product_count = Column(String, nullable=True)
    category_id = Column(Integer, nullable=False)
    category_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    stage_id = Column(String, nullable=False)
    stage_name = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    stage_semantic_id = Column(String, nullable=False)
    stage_semantic = Column(String, nullable=False)
    is_new = Column(String, nullable=False)
    is_recurring = Column(String, nullable=False)
    is_return_customer = Column(String, nullable=False)
    closed = Column(String, nullable=False)
    type_id = Column(String, nullable=True)
    opportunity = Column(Float, nullable=True)
    is_manual_opportunity = Column(String, nullable=False)
    tax_value = Column(Float, nullable=True)
    currency_id = Column(String, nullable=False)
    opportunity_account = Column(Float, nullable=True)
    tax_value_account = Column(String, nullable=False)
    account_currency_id = Column(String, nullable=False)
    probability = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    begindate = Column(DateTime, nullable=False)
    closedate = Column(DateTime, nullable=False)
    location_id = Column(String, nullable=True)
    webform_id = Column(String, nullable=True)
    webform_name = Column(String, nullable=True)
    webform = Column(String, nullable=True)
    source_id = Column(String, nullable=True)
    source_name = Column(String, nullable=True)
    source = Column(String, nullable=True)
    source_description = Column(String, nullable=True)
    originator_id = Column(Integer, nullable=True)
    origin_id = Column(Integer, nullable=True)
    additional_info = Column(String, nullable=True)
    moved_by_id = Column(Integer, nullable=False)
    moved_by_name = Column(String, nullable=False)
    moved_by = Column(String, nullable=False)
    moved_time = Column(DateTime, nullable=False)
    utm_source = Column(String, nullable=True)
    utm_medium = Column(String, nullable=True)
    utm_campaign = Column(String, nullable=True)
    utm_content = Column(String, nullable=True)
    utm_term = Column(String, nullable=True)
    bank_detail_id = Column(Float, nullable=True)
    contact_ids = Column(String, nullable=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<CRMDeal(id={self.id} | name={self.company_name})>'
    
class CRMDealStageHistory(Base):
    """Modelo da tabela 'raw_crm_deal_stage_history' no Banco de Dados."""

    __tablename__ = 'raw_crm_deal_stage_history'

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    type_id = Column(Integer, nullable=False)
    deal_id = Column(Integer, nullable=False)
    date_create = Column(DateTime, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    assigned_by_id = Column(Integer, nullable=False)
    assigned_by_name = Column(String, nullable=False)
    assigned_by = Column(String, nullable=False)
    assigned_by_department = Column(String, nullable=True)
    category_id = Column(Integer, nullable=False)
    category_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    stage_semantic_id = Column(String, nullable=False)
    stage_semantic = Column(String, nullable=False)
    stage_id = Column(String, nullable=False)
    stage_name = Column(String, nullable=True)
    stage = Column(String, nullable=False)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f'<CRMDealStageHistory(id={self.id} | deal_id={self.deal_id})>'
    
class CRMUser(Base):
    """Modelo para a tabela 'raw_user' no Banco de Dados."""

    __tablename__ = 'raw_user'

    id = Column(Integer, nullable=False, primary_key=True, index=True)
    active = Column(String, nullable=False)
    name = Column(String, nullable=True)
    department = Column(String, nullable=True)
    department_ids = Column(String, nullable=False)
    department_id = Column(Integer, nullable=False)
    department_name = Column(String, nullable=False)
    department_id_name = Column(String, nullable=False)
    dep1 = Column(String, nullable=False)
    dep2 = Column(String, nullable=True)
    dep3 = Column(String, nullable=True)
    dep1_id = Column(Integer, nullable=False)
    dep2_id = Column(Float, nullable=True)
    dep3_id = Column(Float, nullable=True)
    dep1_n = Column(String, nullable=False)
    dep2_n = Column(String, nullable=True)
    dep3_n = Column(String, nullable=True)
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<CRMUser(id={self.id} | name={self.name} | active={self.active})>'