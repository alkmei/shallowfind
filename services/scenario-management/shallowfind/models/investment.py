from datetime import datetime
import uuid
from sqlalchemy import (
    JSON,
    UUID,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from .base import Base
from sqlalchemy.orm import relationship, mapped_column, Mapped
from .base import DistributionDict, TaxabilityEnum, AccountTaxStatusEnum


class InvestmentType(Base):
    __tablename__ = "investment_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Expected annual return as JSON distribution
    # Example: {"type": "normal", "mean": 0.07, "stdev": 0.15} or {"type": "fixed", "value": 0.05}
    expected_annual_return: Mapped[DistributionDict] = mapped_column(
        JSON, nullable=False
    )

    # Expense ratio
    expense_ratio: Mapped[float] = mapped_column(Numeric(6, 4), default=0)

    # Expected annual income (dividends/interest) as JSON distribution
    # Example: {"type": "fixed", "value": 0.02} or {"type": "uniform", "lower": 0.01, "upper": 0.03}
    expected_annual_income: Mapped[DistributionDict] = mapped_column(
        JSON, nullable=False
    )

    # Tax status
    taxability: Mapped[TaxabilityEnum] = mapped_column(
        Enum(TaxabilityEnum), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user = relationship("User", back_populates="investment_types")
    investments = relationship("Investment", back_populates="investment_type")


class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    investment_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("investment_types.id"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Current value and cost basis
    current_value: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    cost_basis: Mapped[float] = mapped_column(Numeric(15, 2), default=0)

    # Account tax status
    account_tax_status: Mapped[AccountTaxStatusEnum] = mapped_column(
        Enum(AccountTaxStatusEnum), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    scenario = relationship("Scenario", back_populates="investments")
    investment_type = relationship("InvestmentType", back_populates="investments")
    asset_allocations = relationship(
        "EventAssetAllocation", back_populates="investment"
    )
