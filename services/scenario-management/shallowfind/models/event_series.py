from datetime import datetime
from .base import Base
import uuid
from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship, mapped_column, Mapped
from .base import DistributionDict, EventTypeEnum, AllocationTypeEnum


class EventSeries(Base):
    __tablename__ = "event_series"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Event type
    event_type: Mapped[EventTypeEnum] = mapped_column(
        Enum(EventTypeEnum), nullable=False
    )

    # Start year as JSON distribution
    # Example: {"type": "fixed", "value": 2025} or {"type": "uniform", "lower": 2025, "upper": 2030}
    start_year_distribution: Mapped[DistributionDict] = mapped_column(
        JSON, nullable=False
    )

    # Duration as JSON distribution
    # Example: {"type": "fixed", "value": 30} or {"type": "normal", "mean": 25, "stdev": 3}
    duration_distribution: Mapped[DistributionDict] = mapped_column(
        JSON, nullable=False
    )

    # Reference to another event series (for relative timing)
    reference_event_series_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("event_series.id"), nullable=True
    )

    # Amount configuration (for income/expense events)
    initial_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    # Annual change in amount as JSON distribution
    # Example: {"type": "fixed", "value": 0.03} or {"type": "normal", "mean": 0.025, "stdev": 0.01}
    amount_change_distribution: Mapped[DistributionDict | None] = mapped_column(
        JSON, nullable=True
    )

    # Inflation and tax settings
    inflation_adjusted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Income-specific fields
    is_social_security: Mapped[bool] = mapped_column(Boolean, default=False)
    user_percentage: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Expense-specific fields
    is_discretionary: Mapped[bool] = mapped_column(Boolean, default=False)

    # Investment strategy settings
    maximum_cash: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    scenario = relationship("Scenario", back_populates="event_series")
    reference_event_series = relationship("EventSeries", remote_side=[id])
    asset_allocations = relationship(
        "EventAssetAllocation", back_populates="event_series"
    )


class EventAssetAllocation(Base):
    __tablename__ = "event_asset_allocations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_series_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("event_series.id", ondelete="CASCADE"),
        nullable=False,
    )
    investment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("investments.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Allocation configuration
    allocation_type: Mapped[AllocationTypeEnum] = mapped_column(
        Enum(AllocationTypeEnum), nullable=False
    )
    initial_percentage: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    final_percentage: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )  # For glide paths

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    event_series = relationship("EventSeries", back_populates="asset_allocations")
    investment = relationship("Investment", back_populates="asset_allocations")
