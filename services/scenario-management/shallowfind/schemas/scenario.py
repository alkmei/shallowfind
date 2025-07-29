# schemas/scenario.py
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import uuid

from ..models.base import ScenarioTypeEnum, StatusEnum, PermissionLevelEnum, DistributionDict


class ScenarioBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    scenario_type: ScenarioTypeEnum = ScenarioTypeEnum.individual
    user_birth_year: Optional[int] = Field(None, ge=1900, le=2030)
    spouse_birth_year: Optional[int] = Field(None, ge=1900, le=2030)
    user_life_expectancy: Optional[DistributionDict] = None
    spouse_life_expectancy: Optional[DistributionDict] = None
    financial_goal: float = Field(0, ge=0)
    state_of_residence: Optional[str] = Field(None, min_length=2, max_length=2)
    inflation_assumption: DistributionDict
    annual_contribution_limit: Optional[float] = Field(None, ge=0)

    @field_validator('spouse_birth_year')
    def validate_spouse_birth_year(cls, v, values):
        if values.get('scenario_type') == ScenarioTypeEnum.married_couple and v is None:
            raise ValueError('spouse_birth_year is required for married couples')
        if values.get('scenario_type') == ScenarioTypeEnum.individual and v is not None:
            raise ValueError('spouse_birth_year should not be provided for individuals')
        return v

    @field_validator('spouse_life_expectancy')
    def validate_spouse_life_expectancy(cls, v, values):
        if values.get('scenario_type') == ScenarioTypeEnum.married_couple and v is None:
            raise ValueError('spouse_life_expectancy is required for married couples')
        if values.get('scenario_type') == ScenarioTypeEnum.individual and v is not None:
            raise ValueError('spouse_life_expectancy should not be provided for individuals')
        return v

    @field_validator('state_of_residence')
    def validate_state_code(cls, v):
        if v is not None:
            return v.upper()
        return v


class ScenarioCreate(ScenarioBase):
    """Schema for creating a new scenario (defaults to draft status)."""
    pass


class ScenarioUpdate(BaseModel):
    """Schema for updating a scenario (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    scenario_type: Optional[ScenarioTypeEnum] = None
    user_birth_year: Optional[int] = Field(None, ge=1900, le=2030)
    spouse_birth_year: Optional[int] = Field(None, ge=1900, le=2030)
    user_life_expectancy: Optional[DistributionDict] = None
    spouse_life_expectancy: Optional[DistributionDict] = None
    financial_goal: Optional[float] = Field(None, ge=0)
    state_of_residence: Optional[str] = Field(None, min_length=2, max_length=2)
    inflation_assumption: Optional[DistributionDict] = None
    annual_contribution_limit: Optional[float] = Field(None, ge=0)

    @field_validator('state_of_residence')
    def validate_state_code(cls, v):
        if v is not None:
            return v.upper()
        return v


class ScenarioSharingCreate(BaseModel):
    shared_with_user_id: uuid.UUID
    permission_level: PermissionLevelEnum


class ScenarioSharingResponse(BaseModel):
    id: uuid.UUID
    scenario_id: uuid.UUID
    shared_with_user_id: uuid.UUID
    permission_level: PermissionLevelEnum
    created_at: datetime

    class Config:
        from_attributes = True


class ScenarioResponse(ScenarioBase):
    id: uuid.UUID
    user_id: str
    status: StatusEnum
    sharing_enabled: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    sharing: Optional[List[ScenarioSharingResponse]] = []

    class Config:
        from_attributes = True


class ScenarioListResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    scenario_type: ScenarioTypeEnum
    status: StatusEnum
    sharing_enabled: bool
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScenarioValidationError(BaseModel):
    field: str
    message: str


class ScenarioValidationResponse(BaseModel):
    is_valid: bool
    errors: List[ScenarioValidationError] = []