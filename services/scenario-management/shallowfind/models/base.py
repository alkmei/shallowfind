from typing import Literal, TypedDict, Union
import enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FixedDistributionDict(TypedDict):
    type: Literal["fixed"]
    value: float


class NormalDistributionDict(TypedDict):
    type: Literal["normal"]
    mean: float
    stdev: float


class UniformDistributionDict(TypedDict):
    type: Literal["uniform"]
    lower: float
    upper: float


DistributionDict = Union[
    FixedDistributionDict, NormalDistributionDict, UniformDistributionDict
]


# Enum Definitions
class ScenarioTypeEnum(enum.Enum):
    individual = "individual"
    married_couple = "married_couple"


class StatusEnum(enum.Enum):
    draft = "draft"
    complete = "complete"
    published = "published"


class PermissionLevelEnum(enum.Enum):
    read = "read"
    write = "write"


class AccountTaxStatusEnum(enum.Enum):
    non_retirement = "non_retirement"
    pre_tax_retirement = "pre_tax_retirement"
    after_tax_retirement = "after_tax_retirement"


class EventTypeEnum(enum.Enum):
    income = "income"
    expense = "expense"
    invest = "invest"
    rebalance = "rebalance"


class TaxabilityEnum(enum.Enum):
    taxable = "taxable"
    tax_exempt = "tax_exempt"


class AllocationTypeEnum(enum.Enum):
    fixed = "fixed"
    glide_path = "glide_path"
