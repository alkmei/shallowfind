from .base import Base
import uuid
from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    UUID,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped


class SpendingStrategy(Base):
    __tablename__ = "spending_strategies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    expense_event_series_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("event_series.id", ondelete="CASCADE"),
        nullable=False,
    )
    priority_order: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("scenario_id", "expense_event_series_id"),
        UniqueConstraint("scenario_id", "priority_order"),
    )

    # Relationships
    scenario = relationship("Scenario", back_populates="spending_strategies")


class ExpenseWithdrawalStrategy(Base):
    __tablename__ = "expense_withdrawal_strategies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    investment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("investments.id", ondelete="CASCADE"),
        nullable=False,
    )
    withdrawal_order: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("scenario_id", "investment_id"),
        UniqueConstraint("scenario_id", "withdrawal_order"),
    )

    # Relationships
    scenario = relationship("Scenario", back_populates="expense_withdrawal_strategies")


class RmdStrategy(Base):
    __tablename__ = "rmd_strategies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    investment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("investments.id", ondelete="CASCADE"),
        nullable=False,
    )
    withdrawal_order: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("scenario_id", "investment_id"),
        UniqueConstraint("scenario_id", "withdrawal_order"),
    )

    # Relationships
    scenario = relationship("Scenario", back_populates="rmd_strategies")


class RothConversionStrategy(Base):
    __tablename__ = "roth_conversion_strategies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    investment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("investments.id", ondelete="CASCADE"),
        nullable=False,
    )
    conversion_order: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("scenario_id", "investment_id"),
        UniqueConstraint("scenario_id", "conversion_order"),
    )

    # Relationships
    scenario = relationship("Scenario", back_populates="roth_conversion_strategies")


class RothConversionOptimizerSettings(Base):
    __tablename__ = "roth_conversion_optimizer_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    start_year: Mapped[int] = mapped_column(Integer, nullable=True)
    end_year: Mapped[int] = mapped_column(Integer, nullable=True)

    # Relationships
    scenario = relationship("Scenario", back_populates="roth_optimizer_settings")
