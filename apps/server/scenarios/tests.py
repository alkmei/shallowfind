from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

from .models import (
    Distribution,
    InvestmentType,
    Investment,
    EventSeries,
    AssetAllocation,
    SpendingStrategyItem,
    RMDStrategyItem,
    Scenario,
)


class DistributionModelTest(TestCase):

    def test_fixed_distribution_creation(self):
        """Test creating a valid fixed distribution"""
        dist = Distribution.objects.create(type="fixed", value=100.0)
        self.assertEqual(dist.type, "fixed")
        self.assertEqual(dist.value, 100.0)
        self.assertEqual(str(dist), "Fixed(100.0)")

    def test_normal_distribution_creation(self):
        """Test creating a valid normal distribution"""
        dist = Distribution.objects.create(type="normal", mean=50.0, stdev=10.0)
        self.assertEqual(dist.type, "normal")
        self.assertEqual(dist.mean, 50.0)
        self.assertEqual(dist.stdev, 10.0)
        self.assertEqual(str(dist), "Normal(mean=50.0, stdev=10.0)")

    def test_uniform_distribution_creation(self):
        """Test creating a valid uniform distribution"""
        dist = Distribution.objects.create(type="uniform", lower=10.0, upper=20.0)
        self.assertEqual(dist.type, "uniform")
        self.assertEqual(dist.lower, 10.0)
        self.assertEqual(dist.upper, 20.0)
        self.assertEqual(str(dist), "Uniform(lower=10.0, upper=20.0)")

    def test_fixed_distribution_clean_validation(self):
        """Test that fixed distribution requires value"""
        dist = Distribution(type="fixed")
        with self.assertRaises(ValidationError) as cm:
            dist.full_clean()
        self.assertIn("value", cm.exception.message_dict)

    def test_normal_distribution_clean_validation(self):
        """Test that normal distribution requires mean and stdev"""
        dist = Distribution(type="normal", mean=50.0)
        with self.assertRaises(ValidationError) as cm:
            dist.full_clean()
        self.assertIn("stdev", cm.exception.message_dict)

    def test_normal_distribution_negative_stdev_validation(self):
        """Test that normal distribution rejects negative stdev"""
        dist = Distribution(type="normal", mean=50.0, stdev=-5.0)
        with self.assertRaises(ValidationError) as cm:
            dist.full_clean()
        self.assertIn("stdev", cm.exception.message_dict)

    def test_uniform_distribution_clean_validation(self):
        """Test that uniform distribution requires both bounds"""
        dist = Distribution(type="uniform", lower=10.0)
        with self.assertRaises(ValidationError) as cm:
            dist.full_clean()
        self.assertIn("upper", cm.exception.message_dict)

    def test_uniform_distribution_invalid_bounds(self):
        """Test that uniform distribution rejects lower >= upper"""
        dist = Distribution(type="uniform", lower=20.0, upper=10.0)
        with self.assertRaises(ValidationError) as cm:
            dist.full_clean()
        self.assertIn("upper", cm.exception.message_dict)

    def test_fixed_distribution_extra_fields_validation(self):
        """Test that fixed distribution rejects extra fields"""
        dist = Distribution(type="fixed", value=100.0, mean=50.0)
        with self.assertRaises(ValidationError):
            dist.full_clean()


class InvestmentTypeModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.return_dist = Distribution.objects.create(type="fixed", value=0.06)
        cls.income_dist = Distribution.objects.create(type="fixed", value=0.02)

    def test_investment_type_creation(self):
        """Test creating a valid investment type"""
        inv_type = InvestmentType.objects.create(
            name="S&P 500",
            description="S&P 500 index fund",
            return_amt_or_pct="percent",
            return_distribution=self.return_dist,
            expense_ratio=0.001,
            income_amt_or_pct="percent",
            income_distribution=self.income_dist,
            taxability=True,
        )
        self.assertEqual(inv_type.name, "S&P 500")
        self.assertEqual(str(inv_type), "S&P 500")

    def test_expense_ratio_validation(self):
        """Test expense ratio must be between 0 and 1"""
        inv_type = InvestmentType(
            name="Test",
            description="Test",
            return_amt_or_pct="percent",
            return_distribution=self.return_dist,
            expense_ratio=1.5,  # Invalid: > 1
            income_amt_or_pct="percent",
            income_distribution=self.income_dist,
            taxability=True,
        )
        with self.assertRaises(ValidationError) as cm:
            inv_type.full_clean()
        self.assertIn("expense_ratio", cm.exception.message_dict)

    def test_cash_tax_exempt_validation(self):
        """Test that cash cannot be tax-exempt"""
        inv_type = InvestmentType(
            name="cash",
            description="Cash",
            return_amt_or_pct="amount",
            return_distribution=self.return_dist,
            expense_ratio=0.0,
            income_amt_or_pct="percent",
            income_distribution=self.income_dist,
            taxability=False,  # Invalid for cash
        )
        with self.assertRaises(ValidationError) as cm:
            inv_type.full_clean()
        self.assertIn("taxability", cm.exception.message_dict)


class InvestmentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="testuser@test.com")
        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=Distribution.objects.create(type="fixed", value=80),
            inflation_assumption=Distribution.objects.create(type="fixed", value=0.03),
            after_tax_contribution_limit=7000,
            financial_goal=10000,
            residence_state="NY",
            user=cls.user,
        )

        cls.return_dist = Distribution.objects.create(type="fixed", value=0.06)
        cls.income_dist = Distribution.objects.create(type="fixed", value=0.02)

        cls.stock_type = InvestmentType.objects.create(
            name="S&P 500",
            description="Stock fund",
            return_amt_or_pct="percent",
            return_distribution=cls.return_dist,
            expense_ratio=0.001,
            income_amt_or_pct="percent",
            income_distribution=cls.income_dist,
            taxability=True,
        )

        cls.bond_type = InvestmentType.objects.create(
            name="tax-exempt bonds",
            description="Municipal bonds",
            return_amt_or_pct="percent",
            return_distribution=cls.return_dist,
            expense_ratio=0.001,
            income_amt_or_pct="percent",
            income_distribution=cls.income_dist,
            taxability=False,
        )

        cls.cash_type = InvestmentType.objects.create(
            name="cash",
            description="Cash",
            return_amt_or_pct="amount",
            return_distribution=cls.return_dist,
            expense_ratio=0.0,
            income_amt_or_pct="percent",
            income_distribution=cls.income_dist,
            taxability=True,
        )

    def test_investment_creation(self):
        """Test creating a valid investment"""
        investment = Investment.objects.create(
            scenario=self.scenario,
            investment_type=self.stock_type,
            value=10000.0,
            tax_status="non-retirement",
            investment_id="stocks-1",
        )
        self.assertEqual(investment.value, 10000.0)
        self.assertEqual(str(investment), "stocks-1 (Test Scenario)")

    def test_negative_value_validation(self):
        """Test that investment value cannot be negative"""
        investment = Investment(
            scenario=self.scenario,
            investment_type=self.stock_type,
            value=-1000.0,
            tax_status="non-retirement",
            investment_id="test",
        )
        with self.assertRaises(ValidationError) as cm:
            investment.full_clean()
        self.assertIn("value", cm.exception.message_dict)

    def test_tax_exempt_retirement_account_validation(self):
        """Test that tax-exempt investments cannot be in retirement accounts"""
        investment = Investment(
            scenario=self.scenario,
            investment_type=self.bond_type,  # tax-exempt
            value=5000.0,
            tax_status="pre-tax",  # Invalid combination
            investment_id="bonds-1",
        )
        with self.assertRaises(ValidationError) as cm:
            investment.full_clean()
        self.assertIn("tax_status", cm.exception.message_dict)

    def test_cash_retirement_account_validation(self):
        """Test that cash must be in non-retirement accounts"""
        investment = Investment(
            scenario=self.scenario,
            investment_type=self.cash_type,
            value=1000.0,
            tax_status="pre-tax",  # Invalid for cash
            investment_id="cash-1",
        )
        with self.assertRaises(ValidationError) as cm:
            investment.full_clean()
        self.assertIn("tax_status", cm.exception.message_dict)

    def test_unique_together_constraint(self):
        """Test that scenario + investment_id must be unique"""
        Investment.objects.create(
            scenario=self.scenario,
            investment_type=self.stock_type,
            value=5000.0,
            tax_status="non-retirement",
            investment_id="test-investment",
        )

        # Try to create another with same scenario + investment_id
        with self.assertRaises(ValidationError):
            duplicate = Investment(
                scenario=self.scenario,
                investment_type=self.stock_type,
                value=3000.0,
                tax_status="non-retirement",
                investment_id="test-investment",
            )
            duplicate.full_clean()


class EventSeriesModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="testuser@test.com")
        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=Distribution.objects.create(type="fixed", value=80),
            inflation_assumption=Distribution.objects.create(type="fixed", value=0.03),
            after_tax_contribution_limit=7000,
            financial_goal=10000,
            residence_state="NY",
            user=cls.user,
        )

        cls.start_dist = Distribution.objects.create(type="fixed", value=2025)
        cls.duration_dist = Distribution.objects.create(type="fixed", value=10)
        cls.change_dist = Distribution.objects.create(type="fixed", value=1000)

    def test_income_event_series_creation(self):
        """Test creating a valid income event series"""
        event = EventSeries.objects.create(
            scenario=self.scenario,
            name="salary",
            type="income",
            start_type="distribution",
            start_distribution=self.start_dist,
            duration_distribution=self.duration_dist,
            initial_amount=75000.0,
            change_amt_or_pct="amount",
            change_distribution=self.change_dist,
            inflation_adjusted=True,
            user_fraction=1.0,
            social_security=False,
        )
        self.assertEqual(event.name, "salary")
        self.assertEqual(str(event), "salary (income)")

    def test_start_type_validation(self):
        """Test that start type requires appropriate field"""
        event = EventSeries(
            scenario=self.scenario,
            name="test",
            type="income",
            start_type="distribution",
            start_distribution=None,  # Required but missing
            duration_distribution=self.duration_dist,
            initial_amount=5000.0,
        )
        with self.assertRaises(ValidationError) as cm:
            event.full_clean()
        self.assertIn("start_distribution", cm.exception.message_dict)

    def test_circular_dependency_validation(self):
        """Test that event series cannot depend on itself"""
        event = EventSeries.objects.create(
            scenario=self.scenario,
            name="test-event",
            type="income",
            start_type="distribution",
            start_distribution=self.start_dist,
            duration_distribution=self.duration_dist,
            initial_amount=5000.0,
        )

        event.start_type = "start_with"
        event.start_with_event = event  # Circular dependency
        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_income_initial_amount_required(self):
        """Test that income events require initial amount"""
        event = EventSeries(
            scenario=self.scenario,
            name="salary",
            type="income",
            start_type="distribution",
            start_distribution=self.start_dist,
            duration_distribution=self.duration_dist,
            initial_amount=None,  # Required but missing
        )
        with self.assertRaises(ValidationError) as cm:
            event.full_clean()
        self.assertIn("initial_amount", cm.exception.message_dict)

    def test_user_fraction_validation(self):
        """Test that user fraction must be between 0 and 1"""
        event = EventSeries(
            scenario=self.scenario,
            name="salary",
            type="income",
            start_type="distribution",
            start_distribution=self.start_dist,
            duration_distribution=self.duration_dist,
            initial_amount=75000.0,
            user_fraction=1.5,  # Invalid: > 1
        )
        with self.assertRaises(ValidationError) as cm:
            event.full_clean()
        self.assertIn("user_fraction", cm.exception.message_dict)

    def test_invest_event_validation(self):
        """Test that invest events don't allow income/expense fields"""
        event = EventSeries(
            scenario=self.scenario,
            name="investment",
            type="invest",
            start_type="distribution",
            start_distribution=self.start_dist,
            duration_distribution=self.duration_dist,
            initial_amount=5000.0,  # Should not be set for invest events
            max_cash=1000.0,
        )
        with self.assertRaises(ValidationError) as cm:
            event.full_clean()
        self.assertIn("initial_amount", cm.exception.message_dict)


class AssetAllocationModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="testuser@test.com")
        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=Distribution.objects.create(type="fixed", value=80),
            inflation_assumption=Distribution.objects.create(type="fixed", value=0.03),
            after_tax_contribution_limit=7000,
            financial_goal=10000,
            residence_state="NY",
            user=cls.user,
        )

        cls.investment_type = InvestmentType.objects.create(
            name="S&P 500",
            description="Stock fund",
            return_amt_or_pct="percent",
            return_distribution=Distribution.objects.create(type="fixed", value=0.06),
            expense_ratio=0.001,
            income_amt_or_pct="percent",
            income_distribution=Distribution.objects.create(type="fixed", value=0.02),
            taxability=True,
        )

        cls.investment = Investment.objects.create(
            scenario=cls.scenario,
            investment_type=cls.investment_type,
            value=10000.0,
            tax_status="non-retirement",
            investment_id="stocks-1",
        )

        cls.event_series = EventSeries.objects.create(
            scenario=cls.scenario,
            name="investment",
            type="invest",
            start_type="distribution",
            start_distribution=Distribution.objects.create(type="fixed", value=2025),
            duration_distribution=Distribution.objects.create(type="fixed", value=10),
            max_cash=1000.0,
        )

    def test_asset_allocation_creation(self):
        """Test creating a valid asset allocation"""
        allocation = AssetAllocation.objects.create(
            event_series=self.event_series,
            investment=self.investment,
            percentage=60.0,
            is_final_allocation=False,
        )
        self.assertEqual(allocation.percentage, 60.0)
        self.assertEqual(str(allocation), "investment - stocks-1: 60.0% (Initial)")

    def test_percentage_range_validation(self):
        """Test that percentage must be between 0 and 100"""
        allocation = AssetAllocation(
            event_series=self.event_series,
            investment=self.investment,
            percentage=150.0,  # Invalid: > 100
            is_final_allocation=False,
        )
        with self.assertRaises(ValidationError) as cm:
            allocation.full_clean()
        self.assertIn("percentage", cm.exception.message_dict)

    def test_total_allocation_validation(self):
        """Test that total allocations cannot exceed 100%"""
        # Create first allocation
        AssetAllocation.objects.create(
            event_series=self.event_series,
            investment=self.investment,
            percentage=70.0,
            is_final_allocation=False,
        )

        # Create second investment
        investment2 = Investment.objects.create(
            scenario=self.scenario,
            investment_type=self.investment_type,
            value=5000.0,
            tax_status="non-retirement",
            investment_id="stocks-2",
        )

        # Try to create allocation that would exceed 100%
        allocation2 = AssetAllocation(
            event_series=self.event_series,
            investment=investment2,
            percentage=40.0,  # 70 + 40 = 110% > 100%
            is_final_allocation=False,
        )
        with self.assertRaises(ValidationError) as cm:
            allocation2.full_clean()
        self.assertIn("percentage", cm.exception.message_dict)


class SpendingStrategyItemModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="testuser@test.com")
        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=Distribution.objects.create(type="fixed", value=80),
            inflation_assumption=Distribution.objects.create(type="fixed", value=0.03),
            after_tax_contribution_limit=7000,
            financial_goal=10000,
            residence_state="NY",
            user=cls.user,
        )

        cls.discretionary_expense = EventSeries.objects.create(
            scenario=cls.scenario,
            name="vacation",
            type="expense",
            start_type="distribution",
            start_distribution=Distribution.objects.create(type="fixed", value=2025),
            duration_distribution=Distribution.objects.create(type="fixed", value=10),
            initial_amount=5000.0,
            discretionary=True,
        )

        cls.non_discretionary_expense = EventSeries.objects.create(
            scenario=cls.scenario,
            name="food",
            type="expense",
            start_type="distribution",
            start_distribution=Distribution.objects.create(type="fixed", value=2025),
            duration_distribution=Distribution.objects.create(type="fixed", value=10),
            initial_amount=3000.0,
            discretionary=False,
        )

    def test_spending_strategy_item_creation(self):
        """Test creating a valid spending strategy item"""
        item = SpendingStrategyItem.objects.create(
            scenario=self.scenario, event_series=self.discretionary_expense, order=1
        )
        self.assertEqual(item.order, 1)
        self.assertEqual(str(item), "Test Scenario: 1. vacation")

    def test_non_discretionary_expense_validation(self):
        """Test that only discretionary expenses can be in spending strategy"""
        item = SpendingStrategyItem(
            scenario=self.scenario,
            event_series=self.non_discretionary_expense,  # Not discretionary
            order=1,
        )
        with self.assertRaises(ValidationError) as cm:
            item.full_clean()
        self.assertIn("event_series", cm.exception.message_dict)

    def test_positive_order_validation(self):
        """Test that order must be positive"""
        item = SpendingStrategyItem(
            scenario=self.scenario,
            event_series=self.discretionary_expense,
            order=0,  # Invalid: must be positive
        )
        with self.assertRaises(ValidationError) as cm:
            item.full_clean()
        self.assertIn("order", cm.exception.message_dict)


class RMDStrategyItemModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="testuser@test.com")
        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=Distribution.objects.create(type="fixed", value=80),
            inflation_assumption=Distribution.objects.create(type="fixed", value=0.03),
            after_tax_contribution_limit=7000,
            financial_goal=10000,
            residence_state="NY",
            user=cls.user,
        )

        cls.investment_type = InvestmentType.objects.create(
            name="S&P 500",
            description="Stock fund",
            return_amt_or_pct="percent",
            return_distribution=Distribution.objects.create(type="fixed", value=0.06),
            expense_ratio=0.001,
            income_amt_or_pct="percent",
            income_distribution=Distribution.objects.create(type="fixed", value=0.02),
            taxability=True,
        )

        cls.pre_tax_investment = Investment.objects.create(
            scenario=cls.scenario,
            investment_type=cls.investment_type,
            value=50000.0,
            tax_status="pre-tax",
            investment_id="401k-stocks",
        )

        cls.non_retirement_investment = Investment.objects.create(
            scenario=cls.scenario,
            investment_type=cls.investment_type,
            value=25000.0,
            tax_status="non-retirement",
            investment_id="taxable-stocks",
        )

    def test_rmd_strategy_item_creation(self):
        """Test creating a valid RMD strategy item"""
        item = RMDStrategyItem.objects.create(
            scenario=self.scenario, investment=self.pre_tax_investment, order=1
        )
        self.assertEqual(item.order, 1)
        self.assertEqual(str(item), "Test Scenario: 1. 401k-stocks")

    def test_non_pre_tax_investment_validation(self):
        """Test that only pre-tax investments can be in RMD strategy"""
        item = RMDStrategyItem(
            scenario=self.scenario,
            investment=self.non_retirement_investment,  # Not pre-tax
            order=1,
        )
        with self.assertRaises(ValidationError) as cm:
            item.full_clean()
        self.assertIn("investment", cm.exception.message_dict)


class ScenarioModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="testuser@test.com")
        cls.life_expectancy_dist = Distribution.objects.create(type="fixed", value=80)
        cls.spouse_life_expectancy_dist = Distribution.objects.create(
            type="fixed", value=82
        )
        cls.inflation_dist = Distribution.objects.create(type="fixed", value=0.03)

    def test_individual_scenario_creation(self):
        """Test creating a valid individual scenario"""
        scenario = Scenario.objects.create(
            name="My Retirement Plan",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=self.life_expectancy_dist,
            inflation_assumption=self.inflation_dist,
            after_tax_contribution_limit=7000,
            financial_goal=100000,
            residence_state="NY",
            user=self.user,
        )
        self.assertEqual(scenario.name, "My Retirement Plan")
        self.assertEqual(str(scenario), "My Retirement Plan")

    def test_couple_scenario_creation(self):
        """Test creating a valid couple scenario"""
        scenario = Scenario.objects.create(
            name="Our Retirement Plan",
            marital_status="couple",
            user_birth_year=1985,
            spouse_birth_year=1987,
            user_life_expectancy=self.life_expectancy_dist,
            spouse_life_expectancy=self.spouse_life_expectancy_dist,
            inflation_assumption=self.inflation_dist,
            after_tax_contribution_limit=7000,
            financial_goal=200000,
            residence_state="NY",
            user=self.user,
        )
        self.assertEqual(scenario.marital_status, "couple")
        self.assertEqual(scenario.spouse_birth_year, 1987)

    def test_future_birth_year_validation(self):
        """Test that birth year cannot be in the future"""
        current_year = timezone.now().year
        scenario = Scenario(
            name="Test",
            marital_status="individual",
            user_birth_year=current_year + 1,  # Future year
            user_life_expectancy=self.life_expectancy_dist,
            inflation_assumption=self.inflation_dist,
            after_tax_contribution_limit=7000,
            financial_goal=10000,
            residence_state="NY",
            user=self.user,
        )
        with self.assertRaises(ValidationError) as cm:
            scenario.full_clean()
        self.assertIn("user_birth_year", cm.exception.message_dict)

    def test_couple_missing_spouse_data_validation(self):
        """Test that couple scenarios require spouse data"""
        scenario = Scenario(
            name="Test",
            marital_status="couple",
            user_birth_year=1985,
            spouse_birth_year=None,  # Required for couples
            user_life_expectancy=self.life_expectancy_dist,
            inflation_assumption=self.inflation_dist,
            after_tax_contribution_limit=7000,
            financial_goal=10000,
            residence_state="NY",
            user=self.user,
        )
        with self.assertRaises(ValidationError) as cm:
            scenario.full_clean()
        self.assertIn("spouse_birth_year", cm.exception.message_dict)

    def test_individual_excess_spouse_data_validation(self):
        """Test that individual scenarios reject spouse data"""
        scenario = Scenario(
            name="Test",
            marital_status="individual",
            user_birth_year=1985,
            spouse_birth_year=1987,  # Should not be set for individuals
            user_life_expectancy=self.life_expectancy_dist,
            inflation_assumption=self.inflation_dist,
            after_tax_contribution_limit=7000,
            financial_goal=10000,
            residence_state="NY",
            user=self.user,
        )
        with self.assertRaises(ValidationError) as cm:
            scenario.full_clean()
        self.assertIn("spouse_birth_year", cm.exception.message_dict)

    def test_negative_financial_goal_validation(self):
        """Test that financial goal cannot be negative"""
        scenario = Scenario(
            name="Test",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=self.life_expectancy_dist,
            inflation_assumption=self.inflation_dist,
            after_tax_contribution_limit=7000,
            financial_goal=-5000,  # Invalid: negative
            residence_state="NY",
            user=self.user,
        )
        with self.assertRaises(ValidationError) as cm:
            scenario.full_clean()
        self.assertIn("financial_goal", cm.exception.message_dict)

    def test_roth_conversion_validation(self):
        """Test Roth conversion settings validation"""
        scenario = Scenario(
            name="Test",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=self.life_expectancy_dist,
            inflation_assumption=self.inflation_dist,
            after_tax_contribution_limit=7000,
            financial_goal=10000,
            residence_state="NY",
            roth_conversion_opt=True,
            roth_conversion_start=None,  # Required when opt is True
            user=self.user,
        )
        with self.assertRaises(ValidationError) as cm:
            scenario.full_clean()
        self.assertIn("roth_conversion_start", cm.exception.message_dict)

    def test_invalid_state_validation(self):
        """Test that residence state must be 2 characters"""
        scenario = Scenario(
            name="Test",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=self.life_expectancy_dist,
            inflation_assumption=self.inflation_dist,
            after_tax_contribution_limit=7000,
            financial_goal=10000,
            residence_state="NEW YORK",  # Invalid: not 2 chars
            user=self.user,
        )
        with self.assertRaises(ValidationError) as cm:
            scenario.full_clean()
        self.assertIn("residence_state", cm.exception.message_dict)
