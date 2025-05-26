from django.db import models
from django.core.exceptions import ValidationError
from djmoney.models.fields import MoneyField
from django.utils.translation import gettext_lazy as _
from .enums import USState, MaritalStatus


class Distribution(models.Model):
    FIXED = "fixed"
    NORMAL = "normal"
    UNIFORM = "uniform"
    TYPE_CHOICES = [
        (FIXED, "Fixed"),
        (NORMAL, "Normal"),
        (UNIFORM, "Uniform"),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    value = models.FloatField(null=True, blank=True)
    mean = models.FloatField(null=True, blank=True)
    stdev = models.FloatField(null=True, blank=True)
    lower = models.FloatField(null=True, blank=True)
    upper = models.FloatField(null=True, blank=True)

    is_percentage = models.BooleanField(
        default=False,
        help_text=_("Indicates if the distribution is a percentage."),
    )

    def clean(self):
        # Ensure exactly the fields required by type are set
        if self.type == self.FIXED and self.value is None:
            raise ValidationError({"value": "Fixed distributions require a value."})
        if self.type == self.NORMAL and (self.mean is None or self.stdev is None):
            raise ValidationError("Normal distributions require mean and stdev.")
        if self.type == self.UNIFORM and (self.lower is None or self.upper is None):
            raise ValidationError("Uniform distributions require lower and upper.")


class Scenario(models.Model):
    """
    Represents a financial scenario in the system.
    """

    # Base metadata
    name = models.CharField(max_length=32, unique=True)
    description = models.TextField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    marital_status = models.CharField(
        max_length=1,
        choices=MaritalStatus.choices,
        default=MaritalStatus.SINGLE,
    )

    financial_goal = MoneyField(max_digits=19, decimal_places=4, default_currency="USD")
    residence_state = models.CharField(
        max_length=2, choices=USState.choices, default=USState.NEW_YORK
    )
    after_tax_contribution_limit = MoneyField(
        max_digits=19, decimal_places=4, default_currency="USD", blank=True, null=True
    )

    roth_conversion_enabled = models.BooleanField(
        default=False,
        help_text=_("Enable Roth conversion for this scenario."),
    )

    roth_start_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_("The year to start Roth conversions, if enabled."),
    )

    roth_end_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text=_("The year to end Roth conversions, if enabled."),
    )

    def clean(self):
        if self.roth_conversion_enabled:
            if self.roth_start_year is None:
                raise ValidationError(
                    {
                        "roth_start_year": _(
                            "This field is required when Roth conversion is enabled."
                        )
                    }
                )
            if self.roth_end_year is None:
                raise ValidationError(
                    {
                        "roth_end_year": _(
                            "This field is required when Roth conversion is enabled."
                        )
                    }
                )
            if self.roth_start_year > self.roth_end_year:
                raise ValidationError(
                    {
                        "roth_start_year": _(
                            "Start year cannot be greater than end year."
                        )
                    }
                )

        count = len(self.persons)
        expect = 1 if self.marital_status == self.INDIVIDUAL else 2
        if count != expect or self.life_expectancies.count() != expect:
            msg = f"{self.marital_status} scenarios require {expect} entries."
            raise ValidationError(msg)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Scenario"
        verbose_name_plural = "Scenarios"
        ordering = ["created_at"]


class Person(models.Model):
    """
    Represents a person associated with a financial scenario.
    """

    scenario = models.ForeignKey(
        Scenario, related_name="persons", on_delete=models.CASCADE
    )
    birth_year = models.PositiveIntegerField()
    role = models.CharField(
        max_length=1, choices=Scenario.Role.choices, default=Scenario.Role.PRIMARY
    )
    life_expectancy = models.ForeignKey(
        Distribution, on_delete=models.PROTECT, related_name="+"
    )

    def __str__(self):
        return f"{self.name} ({self.scenario.name})"

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Persons"
        ordering = ["name"]


class InvestmentType(models.Model):
    """
    Represents an investment type associated with a financial scenario.
    """

    scenario = models.ForeignKey(
        Scenario, related_name="investment_types", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=32)
    description = models.TextField(max_length=255, blank=True, default="")

    return_distribution = models.ForeignKey(
        Distribution,
        on_delete=models.PROTECT,
        related_name="+",
    )

    expense_ratio = models.FloatField(
        default=0.0,
        help_text=_("Expense ratio for the investment type, as a percentage."),
    )

    income_distribution = models.ForeignKey(
        Distribution,
        on_delete=models.PROTECT,
        related_name="+",
    )

    taxability = models.BooleanField(
        default=False,
        help_text=_("Indicates if the investment type is taxable."),
    )

    def __str__(self):
        return f"{self.name} ({self.scenario.name})"

    class Meta:
        verbose_name = "Investment Type"
        verbose_name_plural = "Investment Types"
        ordering = ["name"]


class Investment(models.Model):
    NON_RETIRE = "non_retirement"
    PRE_TAX = "pre_tax"
    AFTER_TAX = "after_tax"
    TAX_STATUS_CHOICES = [
        (NON_RETIRE, "Non-Retirement"),
        (PRE_TAX, "Pre-Tax"),
        (AFTER_TAX, "After-Tax"),
    ]

    scenario = models.ForeignKey(
        Scenario, related_name="investments", on_delete=models.CASCADE
    )
    investment_type = models.ForeignKey(
        InvestmentType, related_name="investments", on_delete=models.CASCADE
    )
    value = MoneyField(
        max_digits=19,
        decimal_places=4,
        default_currency="USD",
        help_text=_("Current value of the investment."),
    )

    tax_status = models.CharField(
        max_length=15,
        choices=TAX_STATUS_CHOICES,
        default=NON_RETIRE,
        help_text=_("Tax status of the investment."),
    )


class EventSeries(models.Model):
    """
    Represents a series of events associated with a financial scenario.
    """

    INCOME = "income"
    EXPENSE = "expense"
    INVEST = "invest"
    REBALANCE = "rebalance"
    TYPE_CHOICES = [
        (INCOME, "Income"),
        (EXPENSE, "Expense"),
        (INVEST, "Invest"),
        (REBALANCE, "Rebalance"),
    ]

    START_WITH = "start_with"
    START_AFTER = "start_after"
    START_CHOICES = [
        (Distribution.FIXED, "Fixed"),
        (Distribution.NORMAL, "Normal"),
        (Distribution.UNIFORM, "Uniform"),
        (START_WITH, "Start With"),
        (START_AFTER, "Start After"),
    ]

    scenario = models.ForeignKey(
        Scenario, related_name="event_series", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    start_type = models.CharField(max_length=10, choices=START_CHOICES)
    start_distribution = models.ForeignKey(
        Distribution,
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )
    start_event = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    duration = models.ForeignKey(
        Distribution, on_delete=models.PROTECT, related_name="+"
    )

    # Income/Expense fields
    initial_amount = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )

    expected_annual_change = models.ForeignKey(
        Distribution, on_delete=models.PROTECT, related_name="+", null=True, blank=True
    )
    inflation_adjusted = models.BooleanField(null=True, blank=True)
    user_fraction = models.FloatField(null=True, blank=True)
    is_discretionary = models.BooleanField(null=True, blank=True)
    is_social_security = models.BooleanField(null=True, blank=True)

    # Invest/Rebalance fields
    asset_allocation = models.JSONField(null=True, blank=True)
    glide_path = models.BooleanField(null=True, blank=True)
    asset_allocation_end = models.JSONField(null=True, blank=True)
    max_cash = MoneyField(
        max_digits=14, decimal_places=2, default_currency="USD", null=True, blank=True
    )

    def clean(self):
        errors = {}
        # Income/Expense require financial fields
        if self.type in (self.INCOME, self.EXPENSE):
            for fld in (
                "initial_amount",
                "expected_annual_change",
                "inflation_adjusted",
                "user_fraction",
            ):
                if getattr(self, fld) in (None, ""):
                    errors[fld] = "Required for income/expense series."
        # Expense needs discretionary
        if self.type == self.EXPENSE and self.is_discretionary is None:
            errors["discretionary"] = "Must specify discretionary for expenses."
        # Invest/Rebalance require allocation
        if self.type in (self.INVEST, self.REBALANCE):
            if not self.asset_allocation:
                errors["asset_allocation"] = "Asset allocation required."
            # percentages must sum to 1.0
            if (
                self.asset_allocation
                and abs(sum(self.asset_allocation.values()) - 1.0) > 1e-6
            ):
                errors["asset_allocation"] = "Percentages must sum to 1.0."
        # Glide‐path only for invest
        if self.type == self.INVEST and self.glide_path:
            if not self.asset_allocation_end:
                errors["asset_allocation_end"] = (
                    "End allocation required for glide path."
                )
        if errors:
            raise ValidationError(errors)
