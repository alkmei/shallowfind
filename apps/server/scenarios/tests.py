from django.test import TestCase
from django.core.exceptions import ValidationError
from djmoney.money import Money

from .enums import MaritalStatus

from .models import (
    Distribution,
    Scenario,
    Person,
    AssetAllocation,
    Investment,
    InvestmentAllocation,
    EventSeries,
    InvestmentType,
)


class DistributionModelTest(TestCase):
    def test_fixed_missing_value(self):
        dist = Distribution(type=Distribution.FIXED)
        with self.assertRaises(ValidationError) as cm:
            dist.full_clean()
        self.assertIn("value", cm.exception.error_dict)

    def test_normal_missing_params(self):
        dist = Distribution(type=Distribution.NORMAL, mean=0.1)
        with self.assertRaises(ValidationError):
            dist.full_clean()

    def test_uniform_missing_bounds(self):
        dist = Distribution(type=Distribution.UNIFORM, lower=0, upper=None)
        with self.assertRaises(ValidationError):
            dist.full_clean()

    def test_valid_distributions(self):
        for dtype, kwargs in [
            (Distribution.FIXED, {"value": 1.23}),
            (Distribution.NORMAL, {"mean": 0.05, "stdev": 0.02}),
            (Distribution.UNIFORM, {"lower": 10, "upper": 20}),
        ]:
            d = Distribution(type=dtype, **kwargs)
            # Should not raise
            d.full_clean()


class ScenarioModelTest(TestCase):
    def setUp(self):
        self.sc = Scenario.objects.create(
            name="Test",
            marital_status=MaritalStatus.SINGLE,
            financial_goal=Money(0, "USD"),
            residence_state="NY",
        )

    def test_person_count_for_single(self):
        # No persons yet → invalid for SINGLE
        with self.assertRaises(ValidationError):
            self.sc.full_clean()

        # Add two persons → also invalid
        Person.objects.create(
            scenario=self.sc,
            birth_year=1980,
            role="S",
            life_expectancy=Distribution.objects.create(
                type=Distribution.FIXED, value=80
            ),
        )
        Person.objects.create(
            scenario=self.sc,
            birth_year=1982,
            role="S",
            life_expectancy=Distribution.objects.create(
                type=Distribution.FIXED, value=82
            ),
        )
        with self.assertRaises(ValidationError):
            self.sc.full_clean()

    def test_person_count_for_couple(self):
        self.sc.marital_status = MaritalStatus.MARRIED
        self.sc.save()
        # Only one person → invalid
        Person.objects.create(
            scenario=self.sc,
            birth_year=1980,
            role="S",
            life_expectancy=Distribution.objects.create(
                type=Distribution.FIXED, value=80
            ),
        )
        with self.assertRaises(ValidationError):
            self.sc.full_clean()

    def test_roth_years_required(self):
        # Enable Roth but leave years blank
        self.sc.roth_conversion_enabled = True
        with self.assertRaises(ValidationError) as cm:
            self.sc.full_clean()
        self.assertIn("roth_start_year", cm.exception.error_dict)

    def test_roth_years_range(self):
        self.sc.roth_conversion_enabled = True
        self.sc.roth_start_year = 2055
        self.sc.roth_end_year = 2050
        with self.assertRaises(ValidationError):
            self.sc.full_clean()


class InvestmentAllocationModelTest(TestCase):
    def setUp(self):
        # Create minimal objects needed
        self.alloc_fixed = AssetAllocation.objects.create(type=AssetAllocation.FIXED)
        self.alloc_glide = AssetAllocation.objects.create(
            type=AssetAllocation.GLIDEPATH
        )
        scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status=MaritalStatus.SINGLE,
            financial_goal=Money(0, "USD"),
            residence_state="NY",
        )

        # Create sample distribution fixed
        dist1 = Distribution.objects.create(type=Distribution.FIXED, value=100)
        dist2 = Distribution.objects.create(type=Distribution.FIXED, value=200)

        inv_type = InvestmentType.objects.create(
            name="Test Type",
            description="A test investment type",
            scenario=scenario,
            return_distribution=dist1,
            income_distribution=dist2,
        )

        inv = Investment.objects.create(
            scenario=Scenario.objects.create(
                name="A",
                marital_status=MaritalStatus.SINGLE,
                financial_goal=Money(0, "USD"),
                residence_state="NY",
            ),
            investment_type=inv_type,
            value=Money(100, "USD"),
            tax_status=Investment.NON_RETIRE,
        )
        self.inv = inv

    def test_final_only_for_glide(self):
        ia = InvestmentAllocation(
            asset_allocation=self.alloc_fixed,
            investment=self.inv,
            percentage=1.0,
            role=InvestmentAllocation.FINAL,
        )
        with self.assertRaises(ValidationError):
            ia.full_clean()

        # Should pass for glide-path
        ia.asset_allocation = self.alloc_glide
        ia.full_clean()

    def test_percentages_sum_to_one(self):
        # primary role under glide-path
        ia1 = InvestmentAllocation.objects.create(
            asset_allocation=self.alloc_glide,
            investment=self.inv,
            percentage=0.4,
            role=InvestmentAllocation.PRIMARY,
        )
        ia2 = InvestmentAllocation(
            asset_allocation=self.alloc_glide,
            investment=self.inv,
            percentage=0.7,
            role=InvestmentAllocation.FINAL,
        )
        with self.assertRaises(ValidationError):
            ia2.full_clean()

        # Correct sum
        ia2.percentage = 0.6
        ia2.full_clean()


class EventSeriesModelTest(TestCase):
    def setUp(self):
        sc = Scenario.objects.create(
            name="E",
            marital_status=MaritalStatus.SINGLE,
            financial_goal=Money(0, "USD"),
            residence_state="NY",
        )
        # satisfy person count
        Person.objects.create(
            scenario=sc,
            birth_year=1980,
            role="S",
            life_expectancy=Distribution.objects.create(
                type=Distribution.FIXED, value=80
            ),
        )
        self.sc = sc

    def test_income_missing_fields(self):
        es = EventSeries(
            scenario=self.sc,
            name="Inc",
            type=EventSeries.INCOME,
            start_type=Distribution.FIXED,
            start_distribution=Distribution.objects.create(
                type=Distribution.FIXED, value=2025
            ),
            duration=Distribution.objects.create(type=Distribution.FIXED, value=10),
        )
        # all income-specific fields missing
        with self.assertRaises(ValidationError):
            es.full_clean()

    def test_expense_requires_discretionary(self):
        es = EventSeries(
            scenario=self.sc,
            name="Exp",
            type=EventSeries.EXPENSE,
            start_type=Distribution.FIXED,
            start_distribution=Distribution.objects.create(
                type=Distribution.FIXED, value=2025
            ),
            duration=Distribution.objects.create(type=Distribution.FIXED, value=5),
            initial_amount=Money(100, "USD"),
            expected_annual_change=Distribution.objects.create(
                type=Distribution.FIXED, value=0
            ),
            inflation_adjusted=True,
            user_fraction=1.0,
        )
        # discretionary flag missing
        with self.assertRaises(ValidationError):
            es.full_clean()

    def test_invest_requires_allocation(self):
        es = EventSeries(
            scenario=self.sc,
            name="Inv",
            type=EventSeries.INVEST,
            start_type=Distribution.FIXED,
            start_distribution=Distribution.objects.create(
                type=Distribution.FIXED, value=2025
            ),
            duration=Distribution.objects.create(type=Distribution.FIXED, value=3),
            max_cash=Money(0, "USD"),
        )
        with self.assertRaises(ValidationError):
            es.full_clean()

    def test_rebalance_requires_allocation(self):
        es = EventSeries(
            scenario=self.sc,
            name="Reb",
            type=EventSeries.REBALANCE,
            start_type=Distribution.FIXED,
            start_distribution=Distribution.objects.create(
                type=Distribution.FIXED, value=2025
            ),
            duration=Distribution.objects.create(type=Distribution.FIXED, value=1),
        )
        with self.assertRaises(ValidationError):
            es.full_clean()
