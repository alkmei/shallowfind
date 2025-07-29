from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

from .distribution_types import Distribution


class ScenarioBase(BaseModel):
    name: str
    description: Optional[str] = None
    scenario_type: str
    user_birth_year: Optional[int] = None
    spouse_birth_year: Optional[int] = None
    financial_goal: float = 0
    state_of_residence: Optional[str] = None
    annual_contribution_limit: Optional[float] = None

    # Typed JSON fields
    user_life_expectancy: Optional[Distribution] = None
    spouse_life_expectancy: Optional[Distribution] = None
    inflation_assumption: Distribution

    class Config:
        orm_mode = True


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    user_birth_year: Optional[int] = None
    spouse_birth_year: Optional[int] = None
    financial_goal: Optional[float] = None
    state_of_residence: Optional[str] = None
    annual_contribution_limit: Optional[float] = None

    # Optional distribution updates
    user_life_expectancy: Optional[Distribution] = None
    spouse_life_expectancy: Optional[Distribution] = None
    inflation_assumption: Optional[Distribution] = None


class ScenarioResponse(ScenarioBase):
    id: UUID
    user_id: UUID
    status: str
    sharing_enabled: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
