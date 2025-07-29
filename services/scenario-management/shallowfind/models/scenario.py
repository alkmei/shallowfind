from datetime import datetime
import uuid
from .base import Base
from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    String,
    Text,
    Integer,
    JSON,
    Numeric,
    DateTime,
    UUID,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from .base import DistributionDict, ScenarioTypeEnum, StatusEnum, PermissionLevelEnum


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(
        String(128), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Scenario type and basic info
    scenario_type: Mapped[ScenarioTypeEnum] = mapped_column(
        Enum(ScenarioTypeEnum), default=ScenarioTypeEnum.individual, nullable=False
    )
    user_birth_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    spouse_birth_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Life expectancy distributions as JSON
    # Example: {"type": "fixed", "value": 85} or {"type": "normal", "mean": 85, "stdev": 5}
    user_life_expectancy: Mapped[DistributionDict | None] = mapped_column(
        JSON, nullable=True
    )
    spouse_life_expectancy: Mapped[DistributionDict | None] = mapped_column(
        JSON, nullable=True
    )

    # Financial goal and location
    financial_goal: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    state_of_residence: Mapped[str | None] = mapped_column(String(2), nullable=True)

    # Inflation assumption as JSON distribution
    # Example: {"type": "fixed", "value": 0.03} or {"type": "uniform", "lower": 0.02, "upper": 0.04}
    inflation_assumption: Mapped[DistributionDict] = mapped_column(JSON, nullable=False)

    # Retirement account contribution limits
    annual_contribution_limit: Mapped[float | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )

    # Status and sharing
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum), default=StatusEnum.draft, nullable=False
    )
    sharing_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
    completed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="scenarios")
    sharing = relationship("ScenarioSharing", back_populates="scenario")
    investments = relationship("Investment", back_populates="scenario")
    event_series = relationship("EventSeries", back_populates="scenario")
    spending_strategies = relationship("SpendingStrategy", back_populates="scenario")
    expense_withdrawal_strategies = relationship(
        "ExpenseWithdrawalStrategy", back_populates="scenario"
    )
    rmd_strategies = relationship("RmdStrategy", back_populates="scenario")
    roth_conversion_strategies = relationship(
        "RothConversionStrategy", back_populates="scenario"
    )
    roth_optimizer_settings = relationship(
        "RothConversionOptimizerSettings", back_populates="scenario", uselist=False
    )


class ScenarioSharing(Base):
    __tablename__ = "scenario_sharing"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    shared_with_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    permission_level: Mapped[PermissionLevelEnum] = mapped_column(
        Enum(PermissionLevelEnum), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("scenario_id", "shared_with_user_id"),)

    # Relationships
    scenario = relationship("Scenario", back_populates="sharing")
    shared_with_user = relationship("User", back_populates="shared_scenarios")
