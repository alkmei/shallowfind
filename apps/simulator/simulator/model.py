from enum import Enum
from typing import List, Literal, Optional, Dict, Union
from typing_extensions import Annotated
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from decimal import Decimal

class AccountTaxStatus(str, Enum):
    NON_RETIREMENT = 'non-retirement'
    PRE_TAX_RETIREMENT = 'pre-tax retirement'
    AFTER_TAX_RETIREMENT = 'after-tax retirement'

class EventSeriesType(str, Enum):
    INCOME = 'income'
    EXPENSE = 'expense'
    INVEST = 'invest'
    REBALANCE = 'rebalance'

class InvestmentTaxability(str, Enum):
    TAXABLE = 'taxable'
    TAX_EXEMPT = 'tax-exempt'

class ScenarioStatus(str, Enum):
    DRAFT = 'draft'
    ACTIVE = 'active'
    ARCHIVED = 'archived'

class ScenarioType(str, Enum):
    INDIVIDUAL = 'individual'
    MARRIED = 'married'

class SharePermission(str, Enum):
    READ = 'read'
    WRITE = 'write'

class StartTimingType(str, Enum):
    FIXED = 'fixed'
    DEPENDENT = 'dependent'
    AFTER = 'after'
    SAME_YEAR = 'same_year'

class State(str, Enum):
    NY = 'NY'
    NJ = 'NJ'
    CT = 'CT'
    # Extend as needed

class StrategyType(str, Enum):
    SPENDING = 'spending'
    WITHDRAWAL = 'withdrawal'
    RMD = 'rmd'
    ROTH = 'roth'

class NormalDistribution(BaseModel):
    type: Literal['normal'] 
    mean: float
    stdev: float

class FixedDistribution(BaseModel):
    type: Literal['fixed']
    value: float

class UniformDistribution(BaseModel):
    type: Literal['uniform']
    min: float
    max: float

Distribution = Annotated[Union[NormalDistribution, FixedDistribution, UniformDistribution], Field(discriminator='type')]

class InvestmentType(BaseModel):
    id: UUID4
    scenario_id: UUID4
    name: str
    description: str
    expected_annual_return: Distribution
    return_percent: bool = False
    expense_ratio: Decimal
    expected_annual_income: Distribution
    income_percent: bool = False
    taxability: InvestmentTaxability
    is_cash: bool = False

class Investment(BaseModel):
    id: UUID4
    scenario_id: UUID4
    investment_type_id: UUID4
    name: str
    current_value: Decimal = Decimal('0')
    account_tax_status: AccountTaxStatus

class EventSeries(BaseModel):
    id: UUID4
    scenario_id: UUID4
    name: str
    description: str
    type: EventSeriesType
    # Timing
    start_year: Optional[Distribution]
    duration: Optional[Distribution]
    reference_event_series_id: Optional[UUID4]
    start_timing_type: Optional[StartTimingType]
    is_active: bool = True
    order_index: int
    # Income/Expense fields
    initial_amount: Optional[Decimal]
    annual_change: Optional[Distribution]
    inflation_adjusted: Optional[bool] = False
    user_percentage: Optional[Decimal]
    is_social_security: Optional[bool] = False
    is_discretionary: Optional[bool] = False
    # Invest/Rebalance fields
    asset_allocation: Optional[Dict[str, float]] = None
    is_glide_path: Optional[bool] = False
    initial_allocation: Optional[Dict[int, float]] = None
    final_allocation: Optional[Dict[int, float]] = None
    maximum_cash: Optional[Decimal]
    target_tax_status: Optional[AccountTaxStatus]

class Strategy(BaseModel):
    id: UUID4
    scenario_id: UUID4
    type: StrategyType
    name: str
    description: str
    is_active: bool = True
    ordering: Optional[List[str]] = None

class ScenarioSharing(BaseModel):
    id: UUID4
    scenario_id: UUID4
    user_id: str
    permission: SharePermission

class Scenario(BaseModel):
    id: UUID4
    user_id: str
    title: str
    description: str
    scenario_type: ScenarioType
    scenario_status: ScenarioStatus = ScenarioStatus.DRAFT
    # Personal info
    user_birth_year: int
    spouse_birth_year: Optional[int]
    user_life_expectancy: Optional[Distribution]
    spouse_life_expectancy: Optional[Distribution]
    # Financial settings
    financial_goal: Optional[Decimal]
    state_of_residence: State
    inflation_assumption: Optional[Distribution]
    annual_retirement_contribution_limit: Optional[Decimal]
    # Roth optimizer
    roth_optimizer_enabled: bool = False
    roth_optimizer_start_year: Optional[int]
    roth_optimizer_end_year: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    # Relations
    investment_types: Optional[List[InvestmentType]] = None
    investments: Optional[List[Investment]] = None
    event_series: Optional[List[EventSeries]] = None
    strategies: Optional[List[Strategy]] = None
    shared_with: Optional[List[ScenarioSharing]] = None

Scenario.model_rebuild()
