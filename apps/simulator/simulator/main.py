import numpy as np
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import logging
import copy
from datetime import datetime
from uuid import uuid4

# Import Pydantic models
from model import (
    Scenario,
    InvestmentType,
    Investment,
    EventSeries,
    Strategy,
    AccountTaxStatus,
    EventSeriesType,
    InvestmentTaxability,
    ScenarioStatus,
    ScenarioType,
    State,
    StrategyType,
    StartTimingType,
    Distribution,
    NormalDistribution,
    FixedDistribution,
    UniformDistribution,
)


def sample_distribution(
    distribution: Distribution, rng: np.random.RandomState
) -> float:
    """Sample a value from a Distribution union type."""
    if distribution.type == "fixed":
        return distribution.value
    elif distribution.type == "normal":
        return rng.normal(distribution.mean, distribution.stdev)
    elif distribution.type == "uniform":
        return rng.uniform(distribution.min, distribution.max)
    else:
        raise ValueError(f"Unknown distribution type: {distribution.type}")


@dataclass
class TaxBracket:
    """Federal or state tax bracket."""

    lower_bound: Decimal
    upper_bound: Decimal
    rate: Decimal

    def copy(self):
        return TaxBracket(
            Decimal(str(self.lower_bound)),
            Decimal(str(self.upper_bound)),
            Decimal(str(self.rate)),
        )


@dataclass
class SimulationState:
    """Tracks state during a single simulation run."""

    current_year: int
    user_age: int
    spouse_age: Optional[int] = None
    user_deceased: bool = False
    spouse_deceased: bool = False

    # Annual totals (reset each year)
    cur_year_income: Decimal = Decimal("0")
    cur_year_ss: Decimal = Decimal("0")  # Social security
    cur_year_gains: Decimal = Decimal("0")  # Capital gains
    cur_year_early_withdrawals: Decimal = Decimal("0")

    # Previous year values for tax calculations
    prev_year_income: Decimal = Decimal("0")
    prev_year_ss: Decimal = Decimal("0")
    prev_year_gains: Decimal = Decimal("0")
    prev_year_early_withdrawals: Decimal = Decimal("0")

    # Inflation-adjusted values
    current_inflation_rate: Decimal = Decimal("0")
    annual_contribution_limit: Decimal = Decimal("6500")  # 2024 Roth IRA limit
    standard_deduction: Decimal = Decimal("13850")  # 2024 single

    def reset_annual_totals(self):
        """Reset annual totals at start of new year."""
        self.prev_year_income = self.cur_year_income
        self.prev_year_ss = self.cur_year_ss
        self.prev_year_gains = self.cur_year_gains
        self.prev_year_early_withdrawals = self.cur_year_early_withdrawals

        self.cur_year_income = Decimal("0")
        self.cur_year_ss = Decimal("0")
        self.cur_year_gains = Decimal("0")
        self.cur_year_early_withdrawals = Decimal("0")


class FinancialSimulator:
    """Main simulation engine for lifetime financial planning."""

    def __init__(self, scenario: Scenario, random_seed: Optional[int] = None):
        self.scenario = scenario
        self.rng = np.random.RandomState(random_seed)
        self.logger = logging.getLogger(__name__)

        # Set up default tax brackets and RMD table
        self.federal_tax_brackets = [
            TaxBracket(Decimal("0"), Decimal("10275"), Decimal("0.10")),
            TaxBracket(Decimal("10275"), Decimal("41775"), Decimal("0.12")),
            TaxBracket(Decimal("41775"), Decimal("89450"), Decimal("0.22")),
            TaxBracket(Decimal("89450"), Decimal("190750"), Decimal("0.24")),
            TaxBracket(Decimal("190750"), Decimal("364200"), Decimal("0.32")),
            TaxBracket(Decimal("364200"), Decimal("462500"), Decimal("0.35")),
            TaxBracket(Decimal("462500"), Decimal("999999999"), Decimal("0.37")),
        ]

        self.capital_gains_brackets = [
            TaxBracket(Decimal("0"), Decimal("41775"), Decimal("0.00")),
            TaxBracket(Decimal("41775"), Decimal("459750"), Decimal("0.15")),
            TaxBracket(Decimal("459750"), Decimal("999999999"), Decimal("0.20")),
        ]

        # RMD table (age -> distribution period)
        self.rmd_table: Dict[int, Decimal] = {
            74: Decimal("25.5"),
            75: Decimal("24.6"),
            76: Decimal("23.7"),
            77: Decimal("22.9"),
            78: Decimal("22.0"),
            79: Decimal("21.1"),
            80: Decimal("20.2"),
            85: Decimal("16.8"),
            90: Decimal("12.2"),
            95: Decimal("8.1"),
            100: Decimal("5.4"),
        }

    def run_simulation(self, start_year: int = 2024) -> Dict[str, List[float]]:
        """Run a single simulation and return results."""

        # Initialize simulation state
        state = SimulationState(
            current_year=start_year,
            user_age=start_year - self.scenario.user_birth_year,
            spouse_age=(start_year - self.scenario.spouse_birth_year)
            if self.scenario.spouse_birth_year
            else None,
        )

        # Deep copy investments and event series to avoid modifying originals
        investments = [
            inv.model_copy(deep=True) for inv in (self.scenario.investments or [])
        ]
        event_series = [
            es.model_copy(deep=True) for es in (self.scenario.event_series or [])
        ]

        # Convert investment_types to dict for lookup
        investment_types_dict = {
            it.id: it for it in (self.scenario.investment_types or [])
        }

        # Results tracking
        results: Dict[str, List[float]] = {
            "years": [],
            "total_investments": [],
            "cash_value": [],
            "goal_met": [],
            "income": [],
            "expenses": [],
            "taxes": [],
        }

        # Main simulation loop
        while not self._should_end_simulation(state):
            year_results = self._simulate_year(
                state, investments, event_series, investment_types_dict
            )

            # Record results
            results["years"].append(state.current_year)
            results["total_investments"].append(
                float(self._calculate_total_investments(investments))
            )

            cash_inv = self._get_cash_investment(investments, investment_types_dict)
            results["cash_value"].append(float(cash_inv.current_value))
            results["goal_met"].append(self._is_goal_met(investments))
            results["income"].append(float(state.cur_year_income))
            results["expenses"].append(float(year_results.get("total_expenses", 0)))
            results["taxes"].append(float(year_results.get("total_taxes", 0)))

            # Advance to next year
            state.current_year += 1
            state.user_age += 1
            if state.spouse_age is not None:
                state.spouse_age += 1

            # Check for deaths using life expectancy distributions
            if self.scenario.user_life_expectancy:
                life_exp = sample_distribution(
                    self.scenario.user_life_expectancy, self.rng
                )
                if state.user_age >= life_exp:
                    state.user_deceased = True
            elif state.user_age >= 85:  # Default
                state.user_deceased = True

            if (
                state.spouse_age is not None
                and self.scenario.spouse_life_expectancy is not None
            ):
                spouse_life_exp = sample_distribution(
                    self.scenario.spouse_life_expectancy, self.rng
                )
                if state.spouse_age >= spouse_life_exp:
                    state.spouse_deceased = True

            state.reset_annual_totals()

        return results

    def _simulate_year(
        self,
        state: SimulationState,
        investments: List[Investment],
        event_series: List[EventSeries],
        investment_types_dict: Dict[str, InvestmentType],
    ) -> Dict[str, Decimal]:
        """Simulate a single year of the financial plan."""

        year_results = {}

        # Step 1: Preliminaries
        self._update_inflation_and_tax_data(state)

        # Step 2: Process income events
        self._process_income_events(
            state, event_series, investments, investment_types_dict
        )

        # Step 3: Process RMDs
        self._process_rmds(state, investments, investment_types_dict)

        # Step 4: Update investment values
        self._update_investment_values(state, investments, investment_types_dict)

        # Step 5: Roth conversion optimizer (simplified - not implemented)

        # Step 6: Pay non-discretionary expenses and taxes
        total_expenses, total_taxes = self._pay_expenses_and_taxes(
            state, investments, event_series, investment_types_dict
        )
        year_results["total_expenses"] = total_expenses
        year_results["total_taxes"] = total_taxes

        # Step 7: Pay discretionary expenses
        self._pay_discretionary_expenses(
            state, investments, event_series, investment_types_dict
        )

        # Step 8: Process investment events
        self._process_investment_events(
            state, investments, event_series, investment_types_dict
        )

        # Step 9: Process rebalancing events
        self._process_rebalancing_events(
            state, investments, event_series, investment_types_dict
        )

        return year_results

    def _update_inflation_and_tax_data(self, state: SimulationState):
        """Update inflation rate and tax brackets for current year."""
        # Sample inflation rate
        state.current_inflation_rate = Decimal(
            str(sample_distribution(self.scenario.inflation_assumption, self.rng))
        )

        # Update contribution limits (simplified)
        if self.scenario.annual_retirement_contribution_limit:
            state.annual_contribution_limit = (
                self.scenario.annual_retirement_contribution_limit
            )
        state.annual_contribution_limit *= Decimal("1") + state.current_inflation_rate
        state.standard_deduction *= Decimal("1") + state.current_inflation_rate

    def _process_income_events(
        self,
        state: SimulationState,
        event_series: List[EventSeries],
        investments: List[Investment],
        investment_types_dict: Dict[str, InvestmentType],
    ):
        """Process all income events for the current year."""

        for es in event_series:
            if es.type != EventSeriesType.INCOME or not self._is_event_active_in_year(
                es, state.current_year
            ):
                continue

            # Calculate income amount
            amount = self._calculate_event_amount(es, state)

            # Apply spouse percentages if applicable
            if state.user_deceased and es.user_percentage:
                amount *= Decimal("1") - es.user_percentage
            elif state.spouse_deceased and es.user_percentage:
                amount *= es.user_percentage

            # Add to cash and track totals
            cash_inv = self._get_cash_investment(investments, investment_types_dict)
            cash_inv.current_value += amount
            state.cur_year_income += amount

            if es.is_social_security:
                state.cur_year_ss += amount

    def _process_rmds(
        self,
        state: SimulationState,
        investments: List[Investment],
        investment_types_dict: Dict[str, InvestmentType],
    ):
        """Process Required Minimum Distributions."""

        if state.user_age < 74:
            return

        # Calculate total pre-tax retirement account value
        pre_tax_total = sum(
            inv.current_value
            for inv in investments
            if inv.account_tax_status == AccountTaxStatus.PRE_TAX_RETIREMENT
        )

        if pre_tax_total <= 0:
            return

        # Get distribution period from RMD table
        distribution_period = self.rmd_table.get(
            state.user_age, Decimal("5.4")
        )  # Default to age 100+

        rmd_amount = pre_tax_total / distribution_period

        # Transfer investments in-kind to non-retirement accounts
        remaining_to_transfer = rmd_amount

        for inv in investments:
            if (
                inv.account_tax_status != AccountTaxStatus.PRE_TAX_RETIREMENT
                or remaining_to_transfer <= 0
            ):
                continue

            transfer_amount = min(inv.current_value, remaining_to_transfer)

            # Find investment type
            inv_type = investment_types_dict.get(str(inv.investment_type_id))
            if not inv_type:
                continue

            # Find or create corresponding non-retirement investment
            non_ret_inv = self._find_or_create_investment(
                investments,
                inv_type,
                AccountTaxStatus.NON_RETIREMENT,
                investment_types_dict,
            )

            # Transfer in-kind
            inv.current_value -= transfer_amount
            non_ret_inv.current_value += transfer_amount

            remaining_to_transfer -= transfer_amount

        # RMD counts as taxable income
        state.cur_year_income += rmd_amount

    def _update_investment_values(
        self,
        state: SimulationState,
        investments: List[Investment],
        investment_types_dict: Dict[str, InvestmentType],
    ):
        """Update investment values for annual returns, income, and expenses."""

        for inv in investments:
            inv_type = investment_types_dict.get(str(inv.investment_type_id))
            if not inv_type:
                continue

            beginning_value = inv.current_value

            # Generate income (dividends/interest)
            if (
                inv_type.expected_annual_income.type != "fixed"
                or getattr(inv_type.expected_annual_income, "value", 0) > 0
            ):
                income_amount = Decimal(
                    str(sample_distribution(inv_type.expected_annual_income, self.rng))
                )

                if inv_type.income_percent:
                    generated_income = inv.current_value * income_amount
                else:
                    generated_income = income_amount

                # Add to taxable income if applicable
                if (
                    inv.account_tax_status == AccountTaxStatus.NON_RETIREMENT
                    and inv_type.taxability == InvestmentTaxability.TAXABLE
                ):
                    state.cur_year_income += generated_income

                # Reinvest income
                inv.current_value += generated_income

            # Apply investment returns
            return_amount = Decimal(
                str(sample_distribution(inv_type.expected_annual_return, self.rng))
            )

            if inv_type.return_percent:
                value_change = inv.current_value * return_amount
            else:
                value_change = return_amount

            inv.current_value += value_change

            # Subtract expense ratio
            if inv_type.expense_ratio > 0:
                average_value = (beginning_value + inv.current_value) / Decimal("2")
                expenses = average_value * inv_type.expense_ratio
                inv.current_value -= expenses

            # Ensure non-negative values
            inv.current_value = max(inv.current_value, Decimal("0"))

    def _pay_expenses_and_taxes(
        self,
        state: SimulationState,
        investments: List[Investment],
        event_series: List[EventSeries],
        investment_types_dict: Dict[str, InvestmentType],
    ) -> Tuple[Decimal, Decimal]:
        """Pay non-discretionary expenses and taxes."""

        # Calculate previous year taxes
        fed_tax = self._calculate_federal_income_tax(
            state.prev_year_income, state.prev_year_ss, state.standard_deduction
        )
        cap_gains_tax = self._calculate_capital_gains_tax(state.prev_year_gains)
        early_withdrawal_tax = state.prev_year_early_withdrawals * Decimal("0.10")

        total_taxes = fed_tax + cap_gains_tax + early_withdrawal_tax

        # Calculate non-discretionary expenses
        total_expenses = Decimal("0")
        for es in event_series:
            if (
                es.type != EventSeriesType.EXPENSE
                or (es.is_discretionary is True)
                or not self._is_event_active_in_year(es, state.current_year)
            ):
                continue

            expense_amount = self._calculate_event_amount(es, state)
            total_expenses += expense_amount

        # Total payment needed
        total_payment = total_expenses + total_taxes

        # Withdraw funds if needed
        cash_inv = self._get_cash_investment(investments, investment_types_dict)
        if cash_inv.current_value < total_payment:
            withdrawal_needed = total_payment - cash_inv.current_value
            self._perform_withdrawals(
                state, investments, withdrawal_needed, investment_types_dict
            )

        cash_inv.current_value -= total_payment

        return total_expenses, total_taxes

    def _pay_discretionary_expenses(
        self,
        state: SimulationState,
        investments: List[Investment],
        event_series: List[EventSeries],
        investment_types_dict: Dict[str, InvestmentType],
    ):
        """Pay discretionary expenses subject to financial goal constraint."""

        discretionary_expenses = [
            es
            for es in event_series
            if (
                es.type == EventSeriesType.EXPENSE
                and es.is_discretionary is True
                and self._is_event_active_in_year(es, state.current_year)
            )
        ]

        for es in discretionary_expenses:
            expense_amount = self._calculate_event_amount(es, state)

            # Check if paying this expense would violate financial goal
            current_total = self._calculate_total_investments(investments)
            if current_total - expense_amount >= (
                self.scenario.financial_goal or Decimal("0")
            ):
                # Pay full expense
                payment_amount = expense_amount
            else:
                # Pay partial or skip
                payment_amount = max(
                    Decimal("0"),
                    current_total - (self.scenario.financial_goal or Decimal("0")),
                )

            if payment_amount > 0:
                cash_inv = self._get_cash_investment(investments, investment_types_dict)
                if cash_inv.current_value < payment_amount:
                    withdrawal_needed = payment_amount - cash_inv.current_value
                    self._perform_withdrawals(
                        state, investments, withdrawal_needed, investment_types_dict
                    )

                cash_inv.current_value -= payment_amount

    def _process_investment_events(
        self,
        state: SimulationState,
        investments: List[Investment],
        event_series: List[EventSeries],
        investment_types_dict: Dict[str, InvestmentType],
    ):
        """Process investment/asset allocation events."""

        for es in event_series:
            if es.type != EventSeriesType.INVEST or not self._is_event_active_in_year(
                es, state.current_year
            ):
                continue

            # Calculate excess cash
            cash_inv = self._get_cash_investment(investments, investment_types_dict)
            max_cash = es.maximum_cash or Decimal("0")
            excess_cash = max(Decimal("0"), cash_inv.current_value - max_cash)

            if excess_cash <= 0 or not es.asset_allocation:
                continue

            # Apply asset allocation
            for inv_type_id, percentage in es.asset_allocation.items():
                allocation_amount = excess_cash * Decimal(str(percentage))

                # Find investment type
                inv_type = investment_types_dict.get(inv_type_id)
                if not inv_type:
                    continue

                # Determine target account tax status
                target_status = es.target_tax_status or AccountTaxStatus.NON_RETIREMENT

                # Find or create investment
                target_inv = self._find_or_create_investment(
                    investments, inv_type, target_status, investment_types_dict
                )

                # Make purchase
                target_inv.current_value += allocation_amount
                cash_inv.current_value -= allocation_amount

    def _process_rebalancing_events(
        self,
        state: SimulationState,
        investments: List[Investment],
        event_series: List[EventSeries],
        investment_types_dict: Dict[str, InvestmentType],
    ):
        """Process portfolio rebalancing events."""
        # Simplified implementation - would need more complex logic for full rebalancing
        pass

    def _calculate_federal_income_tax(
        self, income: Decimal, ss_income: Decimal, standard_deduction: Decimal
    ) -> Decimal:
        """Calculate federal income tax using progressive brackets."""
        # 85% of social security is taxable (simplified)
        taxable_ss = ss_income * Decimal("0.85")
        taxable_income = max(Decimal("0"), income - taxable_ss - standard_deduction)

        return self._calculate_progressive_tax(
            taxable_income, self.federal_tax_brackets
        )

    def _calculate_capital_gains_tax(self, capital_gains: Decimal) -> Decimal:
        """Calculate capital gains tax."""
        if capital_gains <= 0:
            return Decimal("0")

        return self._calculate_progressive_tax(
            capital_gains, self.capital_gains_brackets
        )

    def _calculate_progressive_tax(
        self, taxable_amount: Decimal, brackets: List[TaxBracket]
    ) -> Decimal:
        """Calculate tax using progressive brackets."""
        total_tax = Decimal("0")
        remaining_income = taxable_amount

        for bracket in brackets:
            if remaining_income <= 0:
                break

            bracket_income = min(
                remaining_income, bracket.upper_bound - bracket.lower_bound
            )
            bracket_tax = bracket_income * bracket.rate
            total_tax += bracket_tax
            remaining_income -= bracket_income

        return total_tax

    def _calculate_event_amount(
        self, event_series: EventSeries, state: SimulationState
    ) -> Decimal:
        """Calculate the amount for an income or expense event series."""
        if event_series.previous_amount is None:
            amount = event_series.initial_amount or Decimal("0")
        else:
            if event_series.annual_change:
                change = Decimal(
                    str(sample_distribution(event_series.annual_change, self.rng))
                )
                amount = event_series.previous_amount * (Decimal("1") + change)
            else:
                amount = event_series.previous_amount

        if event_series.inflation_adjusted:
            amount *= Decimal("1") + state.current_inflation_rate

        # Apply spouse percentages
        if state.user_deceased and event_series.user_percentage:
            amount *= Decimal("1") - event_series.user_percentage
        elif state.spouse_deceased and event_series.user_percentage:
            amount *= event_series.user_percentage

        event_series.previous_amount = amount
        return amount

    def _perform_withdrawals(
        self,
        state: SimulationState,
        investments: List[Investment],
        amount_needed: Decimal,
        investment_types_dict: Dict[str, InvestmentType],
    ):
        """Perform withdrawals from investments to raise cash."""
        remaining_needed = amount_needed
        cash_inv = self._get_cash_investment(investments, investment_types_dict)

        # Simple withdrawal strategy - withdraw from non-cash investments
        for inv in investments:
            inv_type = investment_types_dict.get(str(inv.investment_type_id))
            if remaining_needed <= 0 or not inv_type or inv_type.is_cash:
                continue

            withdrawal_amount = min(inv.current_value, remaining_needed)

            # Calculate capital gains for non-retirement accounts
            if inv.account_tax_status == AccountTaxStatus.NON_RETIREMENT:
                if inv.current_value > 0:
                    fraction_sold = withdrawal_amount / inv.current_value
                    # Assume cost basis equals current value for simplicity
                    capital_gain = withdrawal_amount * Decimal(
                        "0.2"
                    )  # Simplified gain assumption
                    state.cur_year_gains += capital_gain

            # Add to taxable income for pre-tax retirement withdrawals
            if inv.account_tax_status == AccountTaxStatus.PRE_TAX_RETIREMENT:
                state.cur_year_income += withdrawal_amount

            # Track early withdrawals
            if state.user_age < 59 and inv.account_tax_status in [
                AccountTaxStatus.PRE_TAX_RETIREMENT,
                AccountTaxStatus.AFTER_TAX_RETIREMENT,
            ]:
                state.cur_year_early_withdrawals += withdrawal_amount

            # Perform withdrawal
            inv.current_value -= withdrawal_amount
            cash_inv.current_value += withdrawal_amount
            remaining_needed -= withdrawal_amount

    def _get_cash_investment(
        self,
        investments: List[Investment],
        investment_types_dict: Dict[str, InvestmentType],
    ) -> Investment:
        """Get or create the cash investment."""
        for inv in investments:
            inv_type = investment_types_dict.get(str(inv.investment_type_id))
            if inv_type and inv_type.is_cash:
                return inv

        # Create cash investment if it doesn't exist
        cash_type = InvestmentType(
            id=uuid4(),
            scenario_id=self.scenario.id,
            name="Cash",
            description="Cash holdings",
            expected_annual_return=FixedDistribution(type="fixed", value=0.01),
            return_percent=True,
            expense_ratio=Decimal("0"),
            expected_annual_income=FixedDistribution(type="fixed", value=0.01),
            income_percent=True,
            taxability=InvestmentTaxability.TAXABLE,
            is_cash=True,
        )

        investment_types_dict[str(cash_type.id)] = cash_type

        cash_inv = Investment(
            id=uuid4(),
            scenario_id=self.scenario.id,
            investment_type_id=cash_type.id,
            name="Cash Account",
            current_value=Decimal("0"),
            account_tax_status=AccountTaxStatus.NON_RETIREMENT,
        )
        investments.append(cash_inv)
        return cash_inv

    def _find_or_create_investment(
        self,
        investments: List[Investment],
        investment_type: InvestmentType,
        tax_status: AccountTaxStatus,
        investment_types_dict: Dict[str, InvestmentType],
    ) -> Investment:
        """Find existing investment or create new one."""
        existing = next(
            (
                inv
                for inv in investments
                if inv.investment_type_id == investment_type.id
                and inv.account_tax_status == tax_status
            ),
            None,
        )

        if existing:
            return existing

        # Create new investment
        new_inv = Investment(
            id=uuid4(),
            scenario_id=self.scenario.id,
            investment_type_id=investment_type.id,
            name=f"{investment_type.name} - {tax_status.value}",
            current_value=Decimal("0"),
            account_tax_status=tax_status,
        )
        investments.append(new_inv)
        return new_inv

    def _calculate_total_investments(self, investments: List[Investment]) -> Decimal:
        """Calculate total value of all investments."""
        return sum(inv.current_value for inv in investments)

    def _is_goal_met(self, investments: List[Investment]) -> bool:
        """Check if financial goal is met."""
        financial_goal = self.scenario.financial_goal or Decimal("0")
        return self._calculate_total_investments(investments) >= financial_goal

    def _should_end_simulation(self, state: SimulationState) -> bool:
        """Determine if simulation should end."""
        if state.user_deceased:
            return True
        if state.spouse_deceased and self.scenario.spouse_birth_year is None:
            return True
        return False

    def _is_event_active_in_year(self, event_series: EventSeries, year: int) -> bool:
        """Check if event series is active in given year."""
        if not event_series.is_active:
            return False

        # Handle start year with distributions
        if event_series.start_year is not None:
            if isinstance(event_series.start_year, dict):
                # It's a distribution - sample it
                start_year = int(sample_distribution(event_series.start_year, self.rng))
            else:
                start_year = event_series.start_year

            if year < start_year:
                return False
        else:
            return False

        # Handle duration with distributions
        if event_series.duration is not None:
            if isinstance(event_series.duration, dict):
                # It's a distribution - sample it
                duration = int(sample_distribution(event_series.duration, self.rng))
            else:
                duration = event_series.duration

            return year < start_year + duration

        return True


# Example usage and testing
def create_sample_scenario() -> Scenario:
    """Create a sample scenario for testing."""

    scenario_id = uuid4()

    # Create investment types
    sp500 = InvestmentType(
        id=uuid4(),
        scenario_id=scenario_id,
        name="S&P 500 Index",
        description="Large cap US stocks",
        expected_annual_return=NormalDistribution(type="normal", mean=0.08, stdev=0.15),
        return_percent=True,
        expense_ratio=Decimal("0.003"),
        expected_annual_income=FixedDistribution(type="fixed", value=0.02),
        income_percent=True,
        taxability=InvestmentTaxability.TAXABLE,
    )

    bonds = InvestmentType(
        id=uuid4(),
        scenario_id=scenario_id,
        name="Total Bond Market",
        description="US bond market",
        expected_annual_return=NormalDistribution(type="normal", mean=0.04, stdev=0.05),
        return_percent=True,
        expense_ratio=Decimal("0.002"),
        expected_annual_income=FixedDistribution(type="fixed", value=0.025),
        income_percent=True,
        taxability=InvestmentTaxability.TAXABLE,
    )

    cash = InvestmentType(
        id=uuid4(),
        scenario_id=scenario_id,
        name="Cash",
        description="Cash and money market",
        expected_annual_return=FixedDistribution(type="fixed", value=0.015),
        return_percent=True,
        expense_ratio=Decimal("0"),
        expected_annual_income=FixedDistribution(type="fixed", value=0.015),
        income_percent=True,
        taxability=InvestmentTaxability.TAXABLE,
        is_cash=True,
    )

    # Create initial investments
    investments = [
        Investment(
            id=uuid4(),
            scenario_id=scenario_id,
            investment_type_id=sp500.id,
            name="Initial S&P 500",
            current_value=Decimal("100000"),
            account_tax_status=AccountTaxStatus.NON_RETIREMENT,
        ),
        Investment(
            id=uuid4(),
            scenario_id=scenario_id,
            investment_type_id=bonds.id,
            name="Initial Bonds",
            current_value=Decimal("50000"),
            account_tax_status=AccountTaxStatus.NON_RETIREMENT,
        ),
        Investment(
            id=uuid4(),
            scenario_id=scenario_id,
            investment_type_id=cash.id,
            name="Initial Cash",
            current_value=Decimal("10000"),
            account_tax_status=AccountTaxStatus.NON_RETIREMENT,
        ),
    ]

    # Create event series
    salary = EventSeries(
        id=uuid4(),
        scenario_id=scenario_id,
        name="Salary Income",
        description="Annual salary income",
        type=EventSeriesType.INCOME,
        start_year=FixedDistribution(type="fixed", value=2024),
        duration=FixedDistribution(type="fixed", value=30),  # Work for 30 years
        is_active=True,
        order_index=1,
        initial_amount=Decimal("80000"),
        annual_change=FixedDistribution(type="fixed", value=0.03),
        inflation_adjusted=True,
        user_percentage=Decimal("1.0"),
    )

    retirement_expenses = EventSeries(
        id=uuid4(),
        scenario_id=scenario_id,
        name="Retirement Living Expenses",
        description="Basic living expenses in retirement",
        type=EventSeriesType.EXPENSE,
        start_year=FixedDistribution(
            type="fixed", value=2054
        ),  # Start after salary ends
        duration=None,  # Continue until death
        is_active=True,
        order_index=2,
        initial_amount=Decimal("60000"),
        annual_change=FixedDistribution(type="fixed", value=0.02),
        inflation_adjusted=True,
        is_discretionary=False,
    )

    investment_strategy = EventSeries(
        id=uuid4(),
        scenario_id=scenario_id,
        name="Monthly Investment Strategy",
        description="Automatic investment allocation",
        type=EventSeriesType.INVEST,
        start_year=FixedDistribution(type="fixed", value=2024),
        duration=FixedDistribution(type="fixed", value=30),
        is_active=True,
        order_index=3,
        asset_allocation={str(sp500.id): 0.7, str(bonds.id): 0.3},
        maximum_cash=Decimal("15000"),
        target_tax_status=AccountTaxStatus.NON_RETIREMENT,
    )

    scenario = Scenario(
        id=scenario_id,
        user_id="sample_user",
        title="Sample Retirement Plan",
        description="A sample retirement planning scenario",
        scenario_type=ScenarioType.INDIVIDUAL,
        scenario_status=ScenarioStatus.ACTIVE,
        user_birth_year=1990,
        spouse_birth_year=None,
        user_life_expectancy=FixedDistribution(type="fixed", value=85),
        spouse_life_expectancy=None,
        financial_goal=Decimal("1000000"),
        state_of_residence=State.NY,
        inflation_assumption=NormalDistribution(type="normal", mean=0.025, stdev=0.01),
        annual_retirement_contribution_limit=Decimal("6500"),
        roth_optimizer_enabled=False,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        investment_types=[sp500, bonds, cash],
        investments=investments,
        event_series=[salary, retirement_expenses, investment_strategy],
        strategies=None,
        shared_with=None,
    )

    return scenario


def run_monte_carlo_simulation(
    scenario: Scenario, num_simulations: int = 1000
) -> Dict[str, Any]:
    """Run multiple simulations and aggregate results."""

    all_results = []
    success_rates = []

    for i in range(num_simulations):
        simulator = FinancialSimulator(scenario, random_seed=i)
        results = simulator.run_simulation()
        all_results.append(results)

        # Calculate success rate (percentage of years goal was met)
        if results["goal_met"]:
            success_rate = sum(results["goal_met"]) / len(results["goal_met"])
            success_rates.append(success_rate)

    # Aggregate results
    years = all_results[0]["years"]

    # Calculate percentiles for total investments over time
    investments_by_year = []
    for year_idx in range(len(years)):
        year_values = [
            sim["total_investments"][year_idx]
            for sim in all_results
            if year_idx < len(sim["total_investments"])
        ]
        investments_by_year.append(year_values)

    percentiles = {}
    for p in [10, 25, 50, 75, 90]:
        percentiles[f"p{p}"] = [
            np.percentile(year_vals, p) if year_vals else 0
            for year_vals in investments_by_year
        ]

    # Calculate probability of success over time
    prob_success = []
    for year_idx in range(len(years)):
        year_successes = [
            sim["goal_met"][year_idx]
            for sim in all_results
            if year_idx < len(sim["goal_met"])
        ]
        prob_success.append(
            sum(year_successes) / len(year_successes) if year_successes else 0
        )

    return {
        "years": years,
        "percentiles": percentiles,
        "probability_of_success": prob_success,
        "final_success_rate": np.mean(success_rates) if success_rates else 0,
        "median_final_value": np.median(
            [
                sim["total_investments"][-1]
                for sim in all_results
                if sim["total_investments"]
            ]
        ),
        "simulations": all_results,
    }


def analyze_scenario_sensitivity(
    base_scenario: Scenario,
    parameter_name: str,
    parameter_values: List[float],
    num_simulations: int = 100,
) -> Dict[str, List[Any]]:
    """Analyze sensitivity to a specific parameter."""

    results: Dict[str, List[Any]] = {
        "parameter_values": parameter_values,
        "final_success_rates": [],
        "median_final_values": [],
    }

    for value in parameter_values:
        # Create modified scenario
        scenario = base_scenario.model_copy(deep=True)

        # Modify the specified parameter
        if parameter_name == "inflation_rate":
            scenario.inflation_assumption = FixedDistribution(type="fixed", value=value)
        elif parameter_name == "stock_return":
            for inv_type in scenario.investment_types or []:
                if inv_type.name == "S&P 500 Index":
                    inv_type.expected_annual_return = FixedDistribution(
                        type="fixed", value=value
                    )
        elif parameter_name == "retirement_age":
            # Modify salary duration
            for es in scenario.event_series or []:
                if es.name == "Salary Income":
                    es.duration = FixedDistribution(
                        type="fixed",
                        value=int(value - (2024 - scenario.user_birth_year)),
                    )

        # Run simulations
        mc_results = run_monte_carlo_simulation(scenario, num_simulations)
        results["final_success_rates"].append(mc_results["final_success_rate"])
        results["median_final_values"].append(mc_results["median_final_value"])

    return results


def generate_simulation_report(scenario: Scenario, mc_results: Dict[str, Any]) -> str:
    """Generate a comprehensive simulation report."""

    report = f"""
LIFETIME FINANCIAL PLANNER - SIMULATION REPORT
==============================================

Scenario: {scenario.title}
User Birth Year: {scenario.user_birth_year}
Financial Goal: ${scenario.financial_goal or 0:,.0f}

SIMULATION RESULTS
-----------------
Number of Simulations: {len(mc_results["simulations"])}
Overall Success Rate: {mc_results["final_success_rate"]:.1%}
Median Final Portfolio Value: ${mc_results["median_final_value"]:,.0f}

PORTFOLIO PROJECTIONS (at retirement age 65)
-------------------------------------------
"""

    retirement_year_idx = 65 - (2024 - scenario.user_birth_year)
    if 0 <= retirement_year_idx < len(mc_results["percentiles"]["p50"]):
        report += f"""
10th Percentile: ${mc_results["percentiles"]["p10"][retirement_year_idx]:,.0f}
25th Percentile: ${mc_results["percentiles"]["p25"][retirement_year_idx]:,.0f}
Median (50th):   ${mc_results["percentiles"]["p50"][retirement_year_idx]:,.0f}
75th Percentile: ${mc_results["percentiles"]["p75"][retirement_year_idx]:,.0f}
90th Percentile: ${mc_results["percentiles"]["p90"][retirement_year_idx]:,.0f}

Success Probability at Retirement: {mc_results["probability_of_success"][retirement_year_idx]:.1%}
"""

    report += """

INITIAL PORTFOLIO
----------------
"""
    if scenario.investments:
        total_initial = sum(inv.current_value for inv in scenario.investments)
        for inv in scenario.investments:
            pct = float(inv.current_value / total_initial * 100)
            report += f"{inv.name}: ${inv.current_value:,.0f} ({pct:.1f}%)\n"
        report += f"Total Initial Value: ${total_initial:,.0f}\n"

    report += """

ASSUMPTIONS
-----------
- All calculations ignore state taxes for simplicity
- Standard deduction adjusts with inflation
- 85% of Social Security benefits are taxable
- Early withdrawal penalty: 10% before age 59.5
- RMDs begin at age 74
- Capital gains calculated using average cost basis
- All probability distributions are sampled annually

DISCLAIMERS
-----------
This simulation is for educational purposes only. Results are based on
historical patterns and assumptions that may not hold in the future.
Consult with a qualified financial advisor before making investment decisions.
Past performance does not guarantee future results.
"""

    return report


# Example usage
if __name__ == "__main__":
    # Create and run sample scenario
    scenario = create_sample_scenario()

    # Run single simulation
    simulator = FinancialSimulator(scenario, random_seed=42)
    single_result = simulator.run_simulation()

    print("Single Simulation Results:")
    print(f"Final portfolio value: ${single_result['total_investments'][-1]:,.0f}")
    print(f"Years simulated: {len(single_result['years'])}")
    print(f"Goal met in final year: {single_result['goal_met'][-1]}")

    # Run Monte Carlo analysis
    print("\nRunning Monte Carlo simulation...")
    mc_results = run_monte_carlo_simulation(scenario, num_simulations=100)

    # Generate report
    report = generate_simulation_report(scenario, mc_results)
    print(report)

    # Sensitivity analysis example
    print("\nRunning sensitivity analysis for stock returns...")
    sensitivity = analyze_scenario_sensitivity(
        scenario, "stock_return", [0.06, 0.07, 0.08, 0.09, 0.10], num_simulations=50
    )

    print("Stock Return vs Success Rate:")
    for i, return_rate in enumerate(sensitivity["parameter_values"]):
        success_rate = sensitivity["final_success_rates"][i]
        print(f"{return_rate:.1%}: {success_rate:.1%}")
