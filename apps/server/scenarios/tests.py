from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

from .models import (
    InvestmentType,
    Investment,
    EventSeries,
    AssetAllocation,
    SpendingStrategyItem,
    RMDStrategyItem,
    Scenario,
)

User = get_user_model()


class DistributionJSONFieldTest(TestCase):
    """Test distribution JSON field validation"""

    def test_fixed_distribution_validation(self):
        """Test that fixed distribution validates correctly"""
        user = User.objects.create_user(email="testuser@test.com")

        # Valid fixed distribution
        valid_dist = {
            "type": "fixed",
            "value": 85.0,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=valid_dist,
            inflation_assumption=valid_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
            residence_state="NY",
            user=user,
        )

        self.assertEqual(scenario.user_life_expectancy["type"], "fixed")
        self.assertEqual(scenario.user_life_expectancy["value"], 85.0)

    def test_normal_distribution_validation(self):
        """Test that normal distribution validates correctly"""
        user = User.objects.create_user(email="testuser@test.com")

        # Valid normal distribution
        normal_dist = {
            "type": "normal",
            "value": None,
            "mean": 85.0,
            "stdev": 3.5,
            "lower": None,
            "upper": None,
        }

        fixed_dist = {
            "type": "fixed",
            "value": 0.03,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=normal_dist,
            inflation_assumption=fixed_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
            residence_state="NY",
            user=user,
        )

        self.assertEqual(scenario.user_life_expectancy["type"], "normal")
        self.assertEqual(scenario.user_life_expectancy["mean"], 85.0)
        self.assertEqual(scenario.user_life_expectancy["stdev"], 3.5)

    def test_uniform_distribution_validation(self):
        """Test that uniform distribution validates correctly"""
        user = User.objects.create_user(email="testuser@test.com")

        # Valid uniform distribution
        uniform_dist = {
            "type": "uniform",
            "value": None,
            "mean": None,
            "stdev": None,
            "lower": 2.0,
            "upper": 4.0,
        }

        fixed_dist = {
            "type": "fixed",
            "value": 85.0,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=fixed_dist,
            inflation_assumption=uniform_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
            residence_state="NY",
            user=user,
        )

        self.assertEqual(scenario.inflation_assumption["type"], "uniform")
        self.assertEqual(scenario.inflation_assumption["lower"], 2.0)
        self.assertEqual(scenario.inflation_assumption["upper"], 4.0)


class InvestmentTypeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user and scenario for testing InvestmentType
        cls.user = User.objects.create_user(email="testuser@test.com")

        cls.life_expectancy_dist = {
            "type": "fixed",
            "value": 80,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.inflation_dist = {
            "type": "fixed",
            "value": 0.03,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=cls.life_expectancy_dist,
            inflation_assumption=cls.inflation_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
            residence_state="NY",
            user=cls.user,
        )

    def test_investment_type_creation(self):
        """Test creating a valid investment type"""
        return_dist = {
            "type": "fixed",
            "value": 0.06,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        income_dist = {
            "type": "fixed",
            "value": 0.02,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        inv_type = InvestmentType.objects.create(
            scenario=self.scenario,
            name="S&P 500",
            description="S&P 500 index fund",
            return_amt_or_pct="percent",
            return_distribution=return_dist,
            expense_ratio=0.001,
            income_amt_or_pct="percent",
            income_distribution=income_dist,
            taxability=True,
        )
        self.assertEqual(inv_type.name, "S&P 500")
        self.assertEqual(str(inv_type), "S&P 500")

    def test_expense_ratio_validation(self):
        """Test expense ratio must be between 0 and 1"""
        return_dist = {
            "type": "fixed",
            "value": 0.06,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        income_dist = {
            "type": "fixed",
            "value": 0.02,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        inv_type = InvestmentType(
            scenario=self.scenario,
            name="Test",
            description="Test",
            return_amt_or_pct="percent",
            return_distribution=return_dist,
            expense_ratio=1.5,  # Invalid: > 1
            income_amt_or_pct="percent",
            income_distribution=income_dist,
            taxability=True,
        )
        with self.assertRaises(ValidationError) as cm:
            inv_type.full_clean()
        self.assertIn("expense_ratio", cm.exception.message_dict)

    def test_cash_tax_exempt_validation(self):
        """Test that cash cannot be tax-exempt"""
        return_dist = {
            "type": "fixed",
            "value": 0.06,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        income_dist = {
            "type": "fixed",
            "value": 0.02,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        inv_type = InvestmentType(
            scenario=self.scenario,
            name="cash",
            description="Cash",
            return_amt_or_pct="amount",
            return_distribution=return_dist,
            expense_ratio=0.0,
            income_amt_or_pct="percent",
            income_distribution=income_dist,
            taxability=False,  # Invalid for cash
        )
        with self.assertRaises(ValidationError) as cm:
            inv_type.full_clean()
        self.assertIn("taxability", cm.exception.message_dict)


class InvestmentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="testuser@test.com")

        cls.life_expectancy_dist = {
            "type": "fixed",
            "value": 80,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.inflation_dist = {
            "type": "fixed",
            "value": 0.03,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=cls.life_expectancy_dist,
            inflation_assumption=cls.inflation_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
            residence_state="NY",
            user=cls.user,
        )

        cls.return_dist = {
            "type": "fixed",
            "value": 0.06,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.income_dist = {
            "type": "fixed",
            "value": 0.02,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.stock_type = InvestmentType.objects.create(
            scenario=cls.scenario,
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
            scenario=cls.scenario,
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
            scenario=cls.scenario,
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
            value=Decimal('10000.00'),
            tax_status="non-retirement",
            investment_id="stocks-1",
        )
        self.assertEqual(investment.value, Decimal('10000.00'))
        self.assertEqual(str(investment), "stocks-1 (Test Scenario)")

    def test_negative_value_validation(self):
        """Test that investment value cannot be negative"""
        investment = Investment(
            scenario=self.scenario,
            investment_type=self.stock_type,
            value=Decimal('-1000.00'),
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
            value=Decimal('5000.00'),
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
            value=Decimal('1000.00'),
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
            value=Decimal('5000.00'),
            tax_status="non-retirement",
            investment_id="test-investment",
        )

        # Try to create another with same scenario + investment_id
        with self.assertRaises(ValidationError):
            duplicate = Investment(
                scenario=self.scenario,
                investment_type=self.stock_type,
                value=Decimal('3000.00'),
                tax_status="non-retirement",
                investment_id="test-investment",
            )
            duplicate.full_clean()


class EventSeriesModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="testuser@test.com")

        cls.life_expectancy_dist = {
            "type": "fixed",
            "value": 80,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.inflation_dist = {
            "type": "fixed",
            "value": 0.03,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=cls.life_expectancy_dist,
            inflation_assumption=cls.inflation_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
            residence_state="NY",
            user=cls.user,
        )

        cls.start_dist = {
            "type": "fixed",
            "value": 2025,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.duration_dist = {
            "type": "fixed",
            "value": 10,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.change_dist = {
            "type": "fixed",
            "value": 1000,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

    def test_income_event_series_creation(self):
        """Test creating a valid income event series"""
        event = EventSeries.objects.create(
            scenario=self.scenario,
            name="salary",
            type="income",
            start_type="distribution",
            start_distribution=self.start_dist,
            duration_distribution=self.duration_dist,
            initial_amount=Decimal('75000.00'),
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
            initial_amount=Decimal('5000.00'),
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
            initial_amount=Decimal('5000.00'),
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
            initial_amount=Decimal('75000.00'),
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
            initial_amount=Decimal('5000.00'),  # Should not be set for invest events
            max_cash=Decimal('1000.00'),
        )
        with self.assertRaises(ValidationError) as cm:
            event.full_clean()
        self.assertIn("initial_amount", cm.exception.message_dict)


class AssetAllocationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(email="testuser@test.com")

        cls.life_expectancy_dist = {
            "type": "fixed",
            "value": 80,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.inflation_dist = {
            "type": "fixed",
            "value": 0.03,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=cls.life_expectancy_dist,
            inflation_assumption=cls.inflation_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
            residence_state="NY",
            user=cls.user,
        )

        cls.return_dist = {
            "type": "fixed",
            "value": 0.06,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.income_dist = {
            "type": "fixed",
            "value": 0.02,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.investment_type = InvestmentType.objects.create(
            scenario=cls.scenario,
            name="S&P 500",
            description="Stock fund",
            return_amt_or_pct="percent",
            return_distribution=cls.return_dist,
            expense_ratio=0.001,
            income_amt_or_pct="percent",
            income_distribution=cls.income_dist,
            taxability=True,
        )

        cls.investment = Investment.objects.create(
            scenario=cls.scenario,
            investment_type=cls.investment_type,
            value=Decimal('10000.00'),
            tax_status="non-retirement",
            investment_id="stocks-1",
        )

        cls.start_dist = {
            "type": "fixed",
            "value": 2025,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.duration_dist = {
            "type": "fixed",
            "value": 10,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.event_series = EventSeries.objects.create(
            scenario=cls.scenario,
            name="investment",
            type="invest",
            start_type="distribution",
            start_distribution=cls.start_dist,
            duration_distribution=cls.duration_dist,
            max_cash=Decimal('1000.00'),
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
            value=Decimal('5000.00'),
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

        cls.life_expectancy_dist = {
            "type": "fixed",
            "value": 80,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.inflation_dist = {
            "type": "fixed",
            "value": 0.03,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=cls.life_expectancy_dist,
            inflation_assumption=cls.inflation_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
            residence_state="NY",
            user=cls.user,
        )

        cls.start_dist = {
            "type": "fixed",
            "value": 2025,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.duration_dist = {
            "type": "fixed",
            "value": 10,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.discretionary_expense = EventSeries.objects.create(
            scenario=cls.scenario,
            name="vacation",
            type="expense",
            start_type="distribution",
            start_distribution=cls.start_dist,
            duration_distribution=cls.duration_dist,
            initial_amount=Decimal('5000.00'),
            discretionary=True,
        )

        cls.non_discretionary_expense = EventSeries.objects.create(
            scenario=cls.scenario,
            name="food",
            type="expense",
            start_type="distribution",
            start_distribution=cls.start_dist,
            duration_distribution=cls.duration_dist,
            initial_amount=Decimal('3000.00'),
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

        cls.life_expectancy_dist = {
            "type": "fixed",
            "value": 80,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.inflation_dist = {
            "type": "fixed",
            "value": 0.03,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.scenario = Scenario.objects.create(
            name="Test Scenario",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=cls.life_expectancy_dist,
            inflation_assumption=cls.inflation_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
            residence_state="NY",
            user=cls.user,
        )

        cls.return_dist = {
            "type": "fixed",
            "value": 0.06,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.income_dist = {
            "type": "fixed",
            "value": 0.02,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

        cls.investment_type = InvestmentType.objects.create(
            scenario=cls.scenario,
            name="S&P 500",
            description="Stock fund",
            return_amt_or_pct="percent",
            return_distribution=cls.return_dist,
            expense_ratio=0.001,
            income_amt_or_pct="percent",
            income_distribution=cls.income_dist,
            taxability=True,
        )

        cls.pre_tax_investment = Investment.objects.create(
            scenario=cls.scenario,
            investment_type=cls.investment_type,
            value=Decimal('50000.00'),
            tax_status="pre-tax",
            investment_id="401k-stocks",
        )

        cls.non_retirement_investment = Investment.objects.create(
            scenario=cls.scenario,
            investment_type=cls.investment_type,
            value=Decimal('25000.00'),
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
        cls.life_expectancy_dist = {
            "type": "fixed",
            "value": 80,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }
        cls.spouse_life_expectancy_dist = {
            "type": "fixed",
            "value": 82,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }
        cls.inflation_dist = {
            "type": "fixed",
            "value": 0.03,
            "mean": None,
            "stdev": None,
            "lower": None,
            "upper": None,
        }

    def test_individual_scenario_creation(self):
        """Test creating a valid individual scenario"""
        scenario = Scenario.objects.create(
            name="My Retirement Plan",
            marital_status="individual",
            user_birth_year=1985,
            user_life_expectancy=self.life_expectancy_dist,
            inflation_assumption=self.inflation_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('100000.00'),
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
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('200000.00'),
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
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
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
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
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
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
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
            spouse_life_expectancy=None,
            inflation_assumption=self.inflation_dist,
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('-5000.00'),  # Invalid: negative
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
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
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
            after_tax_contribution_limit=Decimal('7000.00'),
            financial_goal=Decimal('10000.00'),
            residence_state="NEW YORK",  # Invalid: not 2 chars
            user=self.user,
        )
        with self.assertRaises(ValidationError) as cm:
            scenario.full_clean()
        self.assertIn("residence_state", cm.exception.message_dict)