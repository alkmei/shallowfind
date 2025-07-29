from pydantic import BaseModel, Field, ValidationInfo, field_validator
from typing import Union, Literal
from enum import Enum


class DistributionType(str, Enum):
    FIXED = "fixed"
    NORMAL = "normal"
    UNIFORM = "uniform"


class FixedDistribution(BaseModel):
    type: Literal["fixed"]
    value: float


class NormalDistribution(BaseModel):
    type: Literal["normal"]
    mean: float
    stdev: float = Field(gt=0, description="Standard deviation must be positive")


class UniformDistribution(BaseModel):
    type: Literal["uniform"]
    lower: float
    upper: float

    @field_validator("upper")
    def upper_must_be_greater_than_lower(cls, v: float, info: ValidationInfo) -> float:
        if "lower" in info.data and v <= info.data["lower"]:
            raise ValueError("upper must be greater than lower")
        return v


# Union type for all distributions
Distribution = Union[FixedDistribution, NormalDistribution, UniformDistribution]
