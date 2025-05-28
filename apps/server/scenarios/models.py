from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Distribution(models.Model):
    """Base model for representing probability distributions"""

    DISTRIBUTION_TYPES = [
        ("fixed", "Fixed"),
        ("normal", "Normal"),
        ("uniform", "Uniform"),
    ]

    type = models.CharField(max_length=10, choices=DISTRIBUTION_TYPES)

    # For fixed distributions
    value = models.FloatField(null=True, blank=True)

    # For normal distributions
    mean = models.FloatField(null=True, blank=True)
    stdev = models.FloatField(null=True, blank=True)

    # For uniform distributions
    lower = models.FloatField(null=True, blank=True)
    upper = models.FloatField(null=True, blank=True)

    def __str__(self):
        if self.type == "fixed":
            return f"Fixed({self.value})"
        elif self.type == "normal":
            return f"Normal(mean={self.mean}, stdev={self.stdev})"
        elif self.type == "uniform":
            return f"Uniform(lower={self.lower}, upper={self.upper})"


class InvestmentType(models.Model):
    """Defines types of investments (S&P 500, bonds, etc.)"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    # Return configuration
    return_amt_or_pct = models.CharField(
        max_length=10, choices=[("amount", "Amount"), ("percent", "Percent")]
    )
    return_distribution = models.ForeignKey(
        Distribution, on_delete=models.CASCADE, related_name="return_investment_types"
    )

    expense_ratio = models.FloatField()

    # Income configuration
    income_amt_or_pct = models.CharField(
        max_length=10, choices=[("amount", "Amount"), ("percent", "Percent")]
    )
    income_distribution = models.ForeignKey(
        Distribution, on_delete=models.CASCADE, related_name="income_investment_types"
    )

    taxability = models.BooleanField()  # True = taxable, False = tax-exempt

    def __str__(self):
        return self.name


class Investment(models.Model):
    """Individual investment instances"""

    TAX_STATUSES = [
        ("non-retirement", "Non-retirement"),
        ("pre-tax", "Pre-tax Retirement"),
        ("after-tax", "After-tax Retirement"),
    ]

    scenario = models.ForeignKey(
        "Scenario", on_delete=models.CASCADE, related_name="investments"
    )
    investment_type = models.ForeignKey(InvestmentType, on_delete=models.CASCADE)
    value = models.FloatField()
    tax_status = models.CharField(max_length=15, choices=TAX_STATUSES)
    investment_id = models.CharField(max_length=100)  # Unique identifier from YAML

    class Meta:
        unique_together = ["scenario", "investment_id"]

    def __str__(self):
        return f"{self.investment_id} ({self.scenario.name})"


class EventSeries(models.Model):
    """Represents sequences of annual financial events"""

    EVENT_TYPES = [
        ("income", "Income"),
        ("expense", "Expense"),
        ("invest", "Invest"),
        ("rebalance", "Rebalance"),
    ]

    CHANGE_AMT_OR_PCT_CHOICES = [
        ("amount", "Amount"),
        ("percent", "Percent"),
    ]

    START_TYPES = [
        ("distribution", "Distribution"),
        ("start_with", "Start With Event"),
        ("start_after", "Start After Event"),
    ]

    scenario = models.ForeignKey(
        "Scenario", on_delete=models.CASCADE, related_name="event_series"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Start year configuration
    start_type = models.CharField(max_length=20, choices=START_TYPES)
    start_distribution = models.ForeignKey(
        Distribution,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="start_event_series",
    )
    start_with_event = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="start_with_dependents",
    )
    start_after_event = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="start_after_dependents",
    )

    # Duration
    duration_distribution = models.ForeignKey(
        Distribution, on_delete=models.CASCADE, related_name="duration_event_series"
    )

    type = models.CharField(max_length=10, choices=EVENT_TYPES)

    # Income/Expense fields
    initial_amount = models.FloatField(null=True, blank=True)
    change_amt_or_pct = models.CharField(
        max_length=10, choices=CHANGE_AMT_OR_PCT_CHOICES, null=True, blank=True
    )
    change_distribution = models.ForeignKey(
        Distribution,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="change_event_series",
    )
    inflation_adjusted = models.BooleanField(default=False)
    user_fraction = models.FloatField(null=True, blank=True)  # For married couples

    # Income specific
    social_security = models.BooleanField(default=False)

    # Expense specific
    discretionary = models.BooleanField(default=False)

    # Invest/Rebalance specific
    max_cash = models.FloatField(null=True, blank=True)
    glide_path = models.BooleanField(default=False)

    class Meta:
        unique_together = ["scenario", "name"]

    def __str__(self):
        return f"{self.name} ({self.type})"


class AssetAllocation(models.Model):
    """Asset allocation for invest and rebalance events"""

    event_series = models.ForeignKey(
        EventSeries, on_delete=models.CASCADE, related_name="asset_allocations"
    )
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    percentage = models.FloatField()
    is_final_allocation = models.BooleanField(
        default=False
    )  # For glide path final allocation

    class Meta:
        unique_together = ["event_series", "investment", "is_final_allocation"]

    def __str__(self):
        allocation_type = "Final" if self.is_final_allocation else "Initial"
        return f"{self.event_series.name} - {self.investment.investment_id}: {self.percentage}% ({allocation_type})"


class SpendingStrategyItem(models.Model):
    """Discretionary expense ordering for spending strategy"""

    scenario = models.ForeignKey(
        "Scenario", on_delete=models.CASCADE, related_name="spending_strategy_items"
    )
    event_series = models.ForeignKey(EventSeries, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = ["scenario", "event_series"]

    def __str__(self):
        return f"{self.scenario.name}: {self.order}. {self.event_series.name}"


class ExpenseWithdrawalStrategyItem(models.Model):
    """Investment ordering for expense withdrawals"""

    scenario = models.ForeignKey(
        "Scenario",
        on_delete=models.CASCADE,
        related_name="expense_withdrawal_strategy_items",
    )
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = ["scenario", "investment"]

    def __str__(self):
        return f"{self.scenario.name}: {self.order}. {self.investment.investment_id}"


class RMDStrategyItem(models.Model):
    """Pre-tax investment ordering for RMDs"""

    scenario = models.ForeignKey(
        "Scenario", on_delete=models.CASCADE, related_name="rmd_strategy_items"
    )
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = ["scenario", "investment"]

    def __str__(self):
        return f"{self.scenario.name}: {self.order}. {self.investment.investment_id}"


class RothConversionStrategyItem(models.Model):
    """Pre-tax investment ordering for Roth conversions"""

    scenario = models.ForeignKey(
        "Scenario",
        on_delete=models.CASCADE,
        related_name="roth_conversion_strategy_items",
    )
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
        unique_together = ["scenario", "investment"]

    def __str__(self):
        return f"{self.scenario.name}: {self.order}. {self.investment.investment_id}"


class Scenario(models.Model):
    """Main scenario model containing all financial planning information"""

    MARITAL_STATUS_CHOICES = [
        ("individual", "Individual"),
        ("couple", "Couple"),
    ]

    # Basic information
    name = models.CharField(max_length=200)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES)

    # Birth years
    user_birth_year = models.IntegerField()
    spouse_birth_year = models.IntegerField(null=True, blank=True)

    # Life expectancy distributions
    user_life_expectancy = models.ForeignKey(
        Distribution,
        on_delete=models.CASCADE,
        related_name="user_life_expectancy_scenarios",
    )
    spouse_life_expectancy = models.ForeignKey(
        Distribution,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="spouse_life_expectancy_scenarios",
    )

    # Financial settings
    inflation_assumption = models.ForeignKey(
        Distribution, on_delete=models.CASCADE, related_name="inflation_scenarios"
    )
    after_tax_contribution_limit = models.FloatField()
    financial_goal = models.FloatField()
    residence_state = models.CharField(max_length=2)

    # Roth conversion settings
    roth_conversion_opt = models.BooleanField(default=False)
    roth_conversion_start = models.IntegerField(null=True, blank=True)
    roth_conversion_end = models.IntegerField(null=True, blank=True)

    # User ownership and sharing
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_spending_strategy(self):
        """Get ordered list of discretionary expenses"""
        return self.spending_strategy_items.all()

    def get_expense_withdrawal_strategy(self):
        """Get ordered list of investments for expense withdrawals"""
        return self.expense_withdrawal_strategy_items.all()

    def get_rmd_strategy(self):
        """Get ordered list of pre-tax investments for RMDs"""
        return self.rmd_strategy_items.all()

    def get_roth_conversion_strategy(self):
        """Get ordered list of pre-tax investments for Roth conversions"""
        return self.roth_conversion_strategy_items.all()

    class Meta:
        ordering = ["-updated_at"]
