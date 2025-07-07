from typing import TypedDict, Literal, Union, Optional


class FixedDistribution(TypedDict):
    type: Literal["fixed"]
    value: float
    mean: None
    stdev: None
    lower: None
    upper: None


class NormalDistribution(TypedDict):
    type: Literal["normal"]
    value: None
    mean: float
    stdev: float
    lower: None
    upper: None


class UniformDistribution(TypedDict):
    type: Literal["uniform"]
    value: None
    mean: None
    stdev: None
    lower: float
    upper: float


Distribution = Union[FixedDistribution, NormalDistribution, UniformDistribution]
