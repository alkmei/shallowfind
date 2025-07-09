from typing import Dict, Any

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator

from scenarios.types import Distribution

User = get_user_model()

AMOUNT_OR_PERCENT_CHOICES = [
    ("amount", "Amount"),
    ("percent", "Percent"),
]


class DistributionField(models.JSONField):
    """Custom JSONField for distribution data with automatic validation"""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default", dict)
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        if value is not None:
            self._validate_distribution(value)

    def _validate_distribution(self, value: Dict[str, Any]):
        """Validate distribution JSON structure"""
        if not isinstance(value, dict):
            raise ValidationError("Distribution must be a dictionary")

        dist_type = value.get("type")
        if dist_type not in ["fixed", "normal", "uniform"]:
            raise ValidationError(
                "Distribution type must be 'fixed', 'normal', or 'uniform'"
            )

        if dist_type == "fixed":
            if "value" not in value or value["value"] is None:
                raise ValidationError("Fixed distribution requires 'value' field")
            # Ensure other fields are None/not present
            for field in ["mean", "stdev", "lower", "upper"]:
                if value.get(field) is not None:
                    raise ValidationError(
                        f"Fixed distribution should not have '{field}' field"
                    )

        elif dist_type == "normal":
            if "mean" not in value or "stdev" not in value:
                raise ValidationError(
                    "Normal distribution requires 'mean' and 'stdev' fields"
                )
            if value["mean"] is None or value["stdev"] is None:
                raise ValidationError(
                    "Normal distribution mean and stdev cannot be None"
                )
            if value["stdev"] <= 0:
                raise ValidationError(
                    "Normal distribution standard deviation must be positive"
                )
            # Ensure other fields are None/not present
            for field in ["value", "lower", "upper"]:
                if value.get(field) is not None:
                    raise ValidationError(
                        f"Normal distribution should not have '{field}' field"
                    )

        elif dist_type == "uniform":
            if "lower" not in value or "upper" not in value:
                raise ValidationError(
                    "Uniform distribution requires 'lower' and 'upper' fields"
                )
            if value["lower"] is None or value["upper"] is None:
                raise ValidationError("Uniform distribution bounds cannot be None")
            if value["lower"] >= value["upper"]:
                raise ValidationError(
                    "Uniform distribution upper bound must be greater than lower bound"
                )
            # Ensure other fields are None/not present
            for field in ["value", "mean", "stdev"]:
                if value.get(field) is not None:
                    raise ValidationError(
                        f"Uniform distribution should not have '{field}' field"
                    )


class InvestmentType(models.Model):
    """Defines types of investments (S&P 500, bonds, etc.)"""

    name = models.CharField(max_length=100)
    description = models.TextField()

    # Return configuration
    return_amt_or_pct = models.CharField(
        max_length=10, choices=AMOUNT_OR_PERCENT_CHOICES
    )
    return_distribution: Distribution = DistributionField()

    expense_ratio = models.FloatField()

    # Income configuration
    income_amt_or_pct = models.CharField(
        max_length=10, choices=AMOUNT_OR_PERCENT_CHOICES
    )
    income_distribution: Distribution = DistributionField()

    taxability = models.BooleanField()  # True = taxable, False = tax-exempt

    scenario = models.ForeignKey(
        "Scenario", on_delete=models.CASCADE, related_name="investment_types"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["scenario", "name"], name="unique_investment_type_per_scenario"
            )
        ]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        # TODO: Maybe enforce whether income is amt or pct
        # NOTE: Maybe make expense ratio a more reliable type
        if self.expense_ratio < 0 or self.expense_ratio > 1:
            raise ValidationError(
                {"expense_ratio": "Expense ratio must be between 0 and 1 (0% to 100%)."}
            )

        # Is this an actual req?
        if not self.taxability:  # tax-exempt
            if self.name == "cash":
                raise ValidationError(
                    {"taxability": "Cash investment cannot be tax-exempt."}
                )


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
    value = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", validators=[MinValueValidator(0)])
    tax_status = models.CharField(max_length=15, choices=TAX_STATUSES)
    investment_id = models.CharField(max_length=100)  # Unique identifier from YAML

    class Meta:
        unique_together = ["scenario", "investment_id"]

    def __str__(self):
        return f"{self.investment_id} ({self.scenario.name})"

    def clean(self):
        super().clean()

        if self.value.amount < 0:
            raise ValidationError({"value": "Investment value cannot be negative."})

        # Tax-exempt investments should not be in retirement accounts
        if not self.investment_type.taxability and self.tax_status != "non-retirement":
            raise ValidationError(
                {
                    "tax_status": "Tax-exempt investments should only be held in non-retirement accounts."
                }
            )

        # Cash should always be in non-retirement accounts
        if self.investment_type.name == "cash" and self.tax_status != "non-retirement":
            raise ValidationError(
                {"tax_status": "Cash must be held in non-retirement accounts."}
            )


class EventSeries(models.Model):
    """Represents sequences of annual financial events"""

    EVENT_TYPES = [
        ("income", "Income"),
        ("expense", "Expense"),
        ("invest", "Invest"),
        ("rebalance", "Rebalance"),
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
    start_distribution: Distribution = DistributionField(
        null=True, blank=True, default=None
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
    duration_distribution: Distribution = DistributionField()

    type = models.CharField(max_length=10, choices=EVENT_TYPES)

    # Income/Expense fields
    initial_amount = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency="USD",
        null=True,
        blank=True,
        validators=[MinMoneyValidator(0)],
    )
    change_amt_or_pct = models.CharField(
        max_length=10, choices=AMOUNT_OR_PERCENT_CHOICES, null=True, blank=True
    )
    change_distribution: Distribution = DistributionField(
        null=True, blank=True, default=None
    )
    inflation_adjusted = models.BooleanField(default=False)
    user_fraction = models.FloatField(null=True, blank=True)  # For married couples

    # Income specific
    social_security = models.BooleanField(default=False)

    # Expense specific
    discretionary = models.BooleanField(default=False)

    # Invest/Rebalance specific
    max_cash = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency="USD",
        null=True,
        blank=True,
        validators=[MinMoneyValidator(0)],
    )
    glide_path = models.BooleanField(default=False)

    class Meta:
        unique_together = ["scenario", "name"]

    def __str__(self):
        return f"{self.name} ({self.type})"

    def clean(self):
        super().clean()

        # Validate start configuration
        start_fields_set = sum(
            [
                self.start_distribution is not None,
                self.start_with_event is not None,
                self.start_after_event is not None,
            ]
        )

        if self.start_type == "distribution" and self.start_distribution is None:
            raise ValidationError(
                {
                    "start_distribution": "Start distribution is required when start type is distribution."
                }
            )
        elif self.start_type == "start_with" and self.start_with_event is None:
            raise ValidationError(
                {
                    "start_with_event": "Start with event is required when start type is start_with."
                }
            )
        elif self.start_type == "start_after" and self.start_after_event is None:
            raise ValidationError(
                {
                    "start_after_event": "Start after event is required when start type is start_after."
                }
            )

        # Prevent circular dependencies
        if self.start_with_event == self or self.start_after_event == self:
            raise ValidationError("Event series cannot depend on itself.")

        # Type-specific validation
        if self.type in ["income", "expense"]:
            if self.initial_amount is None:
                raise ValidationError(
                    {
                        "initial_amount": f"Initial amount is required for {self.type} events."
                    }
                )
            if self.user_fraction is not None and (
                self.user_fraction < 0 or self.user_fraction > 1
            ):
                raise ValidationError(
                    {"user_fraction": "User fraction must be between 0 and 1."}
                )

        elif self.type in ["invest", "rebalance"]:
            if self.max_cash is None:
                raise ValidationError({"max_cash": "Maximum cash needs to exist."})

            # These fields should not be set for invest/rebalance
            invalid_fields = [
                "initial_amount",
                "change_amt_or_pct",
                "change_distribution",
                "inflation_adjusted",
                "user_fraction",
                "social_security",
                "discretionary",
            ]
            for field in invalid_fields:
                if getattr(self, field) is not None and getattr(self, field) != False:
                    raise ValidationError(
                        {field: f"{field} should not be set for {self.type} events."}
                    )

        # Income-specific validation
        if self.type == "income":
            if hasattr(self, "discretionary") and self.discretionary:
                raise ValidationError(
                    {"discretionary": "Income events cannot be discretionary."}
                )

        # Expense-specific validation
        if self.type == "expense":
            if hasattr(self, "social_security") and self.social_security:
                raise ValidationError(
                    {"social_security": "Only income events can be social security."}
                )


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

    def clean(self):
        super().clean()

        if self.percentage < 0 or self.percentage > 100:
            raise ValidationError(
                {"percentage": "Percentage must be between 0 and 100."}
            )

        # Check that total allocations for this event series sum to 100%
        if self.event_series_id:
            total_percentage = (
                AssetAllocation.objects.filter(
                    event_series=self.event_series,
                    is_final_allocation=self.is_final_allocation,
                )
                .exclude(id=self.id)
                .aggregate(total=models.Sum("percentage"))["total"]
                or 0
            )

            if (
                total_percentage + self.percentage > 100.01
            ):  # Small tolerance for floating point
                raise ValidationError(
                    {
                        "percentage": f"Total allocation would exceed 100%. Current total: {total_percentage}%"
                    }
                )


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

    def clean(self):
        super().clean()

        if self.order <= 0:
            raise ValidationError({"order": "Order must be a positive integer."})

        # Validate that the event series is a discretionary expense
        if not self.event_series.discretionary:
            raise ValidationError(
                {
                    "event_series": "Only discretionary expense event series can be in spending strategy."
                }
            )

        if self.event_series.type != "expense":
            raise ValidationError(
                {
                    "event_series": "Only expense event series can be in spending strategy."
                }
            )


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

    def clean(self):
        super().clean()

        if self.order <= 0:
            raise ValidationError({"order": "Order must be a positive integer."})


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

    def clean(self):
        super().clean()

        if self.order <= 0:
            raise ValidationError({"order": "Order must be a positive integer."})

        if self.investment.tax_status != "pre-tax":
            raise ValidationError(
                {
                    "investment": "Only pre-tax retirement investments can be in RMD strategy."
                }
            )


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

    def clean(self):
        super().clean()

        if self.order <= 0:
            raise ValidationError({"order": "Order must be a positive integer."})

        if self.investment.tax_status != "pre-tax":
            raise ValidationError(
                {
                    "investment": "Only pre-tax retirement investments can be in Roth conversion strategy."
                }
            )


class Scenario(models.Model):
    """Main scenario model containing all financial planning information"""

    US_STATE_CHOICES = [
        ("AL", "Alabama"),
        ("AK", "Alaska"),
        ("AZ", "Arizona"),
        ("AR", "Arkansas"),
        ("CA", "California"),
        ("CO", "Colorado"),
        ("CT", "Connecticut"),
        ("DE", "Delaware"),
        ("FL", "Florida"),
        ("GA", "Georgia"),
        ("HI", "Hawaii"),
        ("ID", "Idaho"),
        ("IL", "Illinois"),
        ("IN", "Indiana"),
        ("IA", "Iowa"),
        ("KS", "Kansas"),
        ("KY", "Kentucky"),
        ("LA", "Louisiana"),
        ("ME", "Maine"),
        ("MD", "Maryland"),
        ("MA", "Massachusetts"),
        ("MI", "Michigan"),
        ("MN", "Minnesota"),
        ("MS", "Mississippi"),
        ("MO", "Missouri"),
        ("MT", "Montana"),
        ("NE", "Nebraska"),
        ("NV", "Nevada"),
        ("NH", "New Hampshire"),
        ("NJ", "New Jersey"),
        ("NM", "New Mexico"),
        ("NY", "New York"),
        ("NC", "North Carolina"),
        ("ND", "North Dakota"),
        ("OH", "Ohio"),
        ("OK", "Oklahoma"),
        ("OR", "Oregon"),
        ("PA", "Pennsylvania"),
        ("RI", "Rhode Island"),
        ("SC", "South Carolina"),
        ("SD", "South Dakota"),
        ("TN", "Tennessee"),
        ("TX", "Texas"),
        ("UT", "Utah"),
        ("VT", "Vermont"),
        ("VA", "Virginia"),
        ("WA", "Washington"),
        ("WV", "West Virginia"),
        ("WI", "Wisconsin"),
        ("WY", "Wyoming"),
    ]

    MARITAL_STATUS_CHOICES = [
        ("individual", "Individual"),
        ("couple", "Couple"),
    ]

    # Basic information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True, max_length=1000)
    marital_status = models.CharField(
        max_length=10, choices=MARITAL_STATUS_CHOICES, default="individual"
    )

    # Birth years
    user_birth_year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(timezone.now().year)]
    )
    spouse_birth_year = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1900), MaxValueValidator(timezone.now().year)],
    )

    # Life expectancy distributions
    user_life_expectancy: Distribution = DistributionField()
    spouse_life_expectancy: Distribution = DistributionField(
        null=True, blank=True, default=None
    )

    # Financial settings
    inflation_assumption: Distribution = DistributionField()
    after_tax_contribution_limit = MoneyField(
        max_digits=10, decimal_places=2, default_currency="USD", validators=[MinValueValidator(0)]
    )
    financial_goal = MoneyField(max_digits=14, decimal_places=2, default_currency="USD", validators=[MinValueValidator(0)])
    residence_state = models.CharField(max_length=2, choices=US_STATE_CHOICES)

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

    def clean(self):
        super().clean()

        current_year = timezone.now().year

        # Birth year validation
        if self.user_birth_year > current_year:
            raise ValidationError(
                {"user_birth_year": "Birth year cannot be in the future."}
            )

        if self.user_birth_year < 1900:
            raise ValidationError({"user_birth_year": "Birth year seems unrealistic."})

        if self.user_life_expectancy["type"] == "uniform":
            raise ValidationError(
                {
                    "user_life_expectancy": "User life expectancy cannot be uniform distribution."
                }
            )

        # Couple-specific validation
        if self.marital_status == "couple":
            if self.spouse_birth_year is None:
                raise ValidationError(
                    {"spouse_birth_year": "Spouse birth year is required for couples."}
                )

            if self.spouse_life_expectancy is None:
                raise ValidationError(
                    {
                        "spouse_life_expectancy": "Spouse life expectancy is required for couples."
                    }
                )

            if self.spouse_birth_year > current_year:
                raise ValidationError(
                    {"spouse_birth_year": "Spouse birth year cannot be in the future."}
                )

            if self.spouse_birth_year < 1900:
                raise ValidationError(
                    {"spouse_birth_year": "Spouse birth year seems unrealistic."}
                )

            if self.spouse_life_expectancy["type"] == "uniform":
                raise ValidationError(
                    {
                        "spouse_life_expectancy": "Spouse life expectancy cannot be uniform distribution."
                    }
                )

        elif self.marital_status == "individual":
            if self.spouse_birth_year is not None:
                raise ValidationError(
                    {
                        "spouse_birth_year": "Spouse birth year should not be set for individuals."
                    }
                )

            if self.spouse_life_expectancy is not None:
                raise ValidationError(
                    {
                        "spouse_life_expectancy": "Spouse life expectancy should not be set for individuals."
                    }
                )

        # Financial validation
        if self.financial_goal.amount < 0:
            raise ValidationError(
                {"financial_goal": "Financial goal cannot be negative."}
            )

        if self.after_tax_contribution_limit.amount < 0:
            raise ValidationError(
                {
                    "after_tax_contribution_limit": "Contribution limit cannot be negative."
                }
            )

        # Roth conversion validation
        if self.roth_conversion_opt:
            if self.roth_conversion_start is None or self.roth_conversion_end is None:
                raise ValidationError(
                    {
                        "roth_conversion_start": "Start and end years required when Roth conversion is enabled.",
                        "roth_conversion_end": "Start and end years required when Roth conversion is enabled.",
                    }
                )

            if self.roth_conversion_start >= self.roth_conversion_end:
                raise ValidationError(
                    {"roth_conversion_end": "End year must be after start year."}
                )

            if self.roth_conversion_start < current_year:
                raise ValidationError(
                    {
                        "roth_conversion_start": "Roth conversion start year cannot be in the past."
                    }
                )
