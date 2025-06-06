from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from djmoney.models.fields import MoneyField

User = get_user_model()

AMOUNT_OR_PERCENT_CHOICES = [
    ("amount", "Amount"),
    ("percent", "Percent"),
]


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

    def clean(self):
        super().clean()

        if self.type == "fixed":
            if self.value is None:
                raise ValidationError(
                    {"value": "Value is required for fixed distributions."}
                )
            if (
                self.mean is not None
                or self.stdev is not None
                or self.lower is not None
                or self.upper is not None
            ):
                raise ValidationError(
                    "Only value should be set for fixed distributions."
                )

        elif self.type == "normal":
            if self.mean is None or self.stdev is None:
                raise ValidationError(
                    {
                        "mean": "Mean and standard deviation are required for normal distributions.",
                        "stdev": "Mean and standard deviation are required for normal distributions.",
                    }
                )
            if self.stdev <= 0:
                raise ValidationError({"stdev": "Standard deviation must be positive."})
            if (
                self.value is not None
                or self.lower is not None
                or self.upper is not None
            ):
                raise ValidationError(
                    "Only mean and stdev should be set for normal distributions."
                )

        elif self.type == "uniform":
            if self.lower is None or self.upper is None:
                raise ValidationError(
                    {
                        "lower": "Lower and upper bounds are required for uniform distributions.",
                        "upper": "Lower and upper bounds are required for uniform distributions.",
                    }
                )
            if self.lower >= self.upper:
                raise ValidationError(
                    {"upper": "Upper bound must be greater than lower bound."}
                )
            if (
                self.value is not None
                or self.mean is not None
                or self.stdev is not None
            ):
                raise ValidationError(
                    "Only lower and upper should be set for uniform distributions."
                )


class InvestmentType(models.Model):
    """Defines types of investments (S&P 500, bonds, etc.)"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    # Return configuration
    return_amt_or_pct = models.CharField(
        max_length=10, choices=AMOUNT_OR_PERCENT_CHOICES
    )
    return_distribution = models.ForeignKey(
        Distribution, on_delete=models.CASCADE, related_name="return_investment_types"
    )

    expense_ratio = models.FloatField()

    # Income configuration
    income_amt_or_pct = models.CharField(
        max_length=10, choices=AMOUNT_OR_PERCENT_CHOICES
    )
    income_distribution = models.ForeignKey(
        Distribution, on_delete=models.CASCADE, related_name="income_investment_types"
    )

    taxability = models.BooleanField()  # True = taxable, False = tax-exempt

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
    value = MoneyField(max_digits=14, decimal_places=2, default_currency="USD")
    tax_status = models.CharField(max_length=15, choices=TAX_STATUSES)
    investment_id = models.CharField(max_length=100)  # Unique identifier from YAML

    class Meta:
        unique_together = ["scenario", "investment_id"]

    def __str__(self):
        return f"{self.investment_id} ({self.scenario.name})"

    def clean(self):
        super().clean()

        if self.value < 0:
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
    initial_amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )
    change_amt_or_pct = models.CharField(
        max_length=10, choices=AMOUNT_OR_PERCENT_CHOICES, null=True, blank=True
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
    max_cash = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
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
            if self.initial_amount < 0:
                raise ValidationError(
                    {"initial_amount": "Initial amount cannot be negative."}
                )

            if self.user_fraction is not None and (
                self.user_fraction < 0 or self.user_fraction > 1
            ):
                raise ValidationError(
                    {"user_fraction": "User fraction must be between 0 and 1."}
                )

        elif self.type in ["invest", "rebalance"]:
            if self.max_cash is not None and self.max_cash < 0:
                raise ValidationError({"max_cash": "Maximum cash cannot be negative."})

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
    after_tax_contribution_limit = MoneyField(
        max_digits=10, decimal_places=2, default_currency="USD"
    )
    financial_goal = MoneyField(max_digits=14, decimal_places=2, default_currency="USD")
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
        if self.financial_goal < 0:
            raise ValidationError(
                {"financial_goal": "Financial goal cannot be negative."}
            )

        if self.after_tax_contribution_limit < 0:
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
