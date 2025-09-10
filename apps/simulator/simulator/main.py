import numpy as np
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime
from .model import (
    Scenario, Distribution, FixedDistribution, AccountTaxStatus,
    EventSeriesType, InvestmentTaxability
)

# Assume Pydantic models Scenario, EventSeries, InvestmentType, Investment, Strategy, Distribution etc. are imported

def sample_distribution(dist: Optional[Distribution], rng: np.random.Generator) -> float:
    """Sample a numeric value from the given distribution."""
    if dist is None:
        return 0.0
    if dist.type == 'fixed':
        return dist.value
    elif dist.type == 'normal':
        return rng.normal(dist.mean, dist.stdev)
    elif dist.type == 'uniform':
        return rng.uniform(dist.min, dist.max)
    else:
        raise ValueError(f"Unknown distribution type: {dist.type}")

def inflation_adjust_value(value: float, inflation_rate: float, years: int) -> float:
    """Adjust a value for inflation for a number of years."""
    return value * ((1 + inflation_rate) ** years)

class Simulation:
    def __init__(self, scenario: Scenario, seed: Optional[int] = None):
        self.scenario = scenario
        self.rng = np.random.default_rng(seed)
        self.current_year = datetime.now().year
        self.end_year = self.scenario.user_birth_year + int(self._get_life_expectancy(self.scenario.user_life_expectancy))
        # Tracking investment values by investment ID
        self.investments: Dict[str, Decimal] = {inv.id.hex: inv.current_value for inv in self.scenario.investments or []}
        # Keep track of purchase prices for capital gain calculation (start as current_value)
        self.purchase_prices: Dict[str, Decimal] = self.investments.copy()
        # Initialize other running totals
        self.curYearIncome = 0.0
        self.curYearSS = 0.0
        self.curYearGains = 0.0
        self.curYearEarlyWithdrawals = 0.0
        self.standard_deduction = 13850  # Example fixed, replace with user/state/year-dependent
        self.inflation_rate = 0.02  # Assume 2%, or sample from assumption each year
        
    def _get_life_expectancy(self, dist: Optional[Distribution]) -> float:
        if dist is None:
            return 85  # default fallback
        return sample_distribution(dist, self.rng)
    
    def run(self):
        year = self.current_year
        while year < self.end_year:
            age = year - self.scenario.user_birth_year
            print(f"Simulating year {year}, user age {age}")
            
            # 1. Sample inflation rate if stochastic
            self.inflation_rate = sample_distribution(self.scenario.inflation_assumption, self.rng) if self.scenario.inflation_assumption else 0.02
            
            # 2. Run income events: add income to cash investment
            self._run_income_events(year)
            
            # 3. Perform RMD for previous year if applicable
            if age >= 74:
                self._perform_rmd(year - 1)
            
            # 4. Update investments with returns, dividends, expenses
            self._update_investments(year)
            
            # 5. Roth conversion optimizer if enabled
            if self.scenario.roth_optimizer_enabled:
                self._run_roth_conversion(year, age)
            
            # 6. Pay non-discretionary expenses + previous year’s taxes
            self._pay_expenses(year, discretionary=False)
            
            # 7. Pay discretionary expenses if goals not violated
            self._pay_expenses(year, discretionary=True)
            
            # 8. Run invest events
            self._run_invest_events(year)
            
            # 9. Run rebalance events
            self._run_rebalance_events(year)
            
            # Advance to next year
            year += 1
            
        print("Simulation ended.")
        
    def _run_income_events(self, year: int):
        income_events = [e for e in self.scenario.event_series or [] if e.type == EventSeriesType.INCOME]
        total_income = 0.0
        for event in income_events:
            start_year = int(sample_distribution(event.start_year, self.rng)) if event.start_year else self.current_year
            duration = int(sample_distribution(event.duration, self.rng)) if event.duration else 1
            if start_year <= year < start_year + duration:
                amount = float(event.initial_amount or 0)
                # Apply annual changes while active
                years_active = year - start_year
                if event.annual_change:
                    annual_change = sample_distribution(event.annual_change, self.rng)
                    if isinstance(event.annual_change, FixedDistribution) and event.inflation_adjusted:
                        # Fixed + inflation adjustment
                        amount = amount * ((1 + annual_change + self.inflation_rate) ** years_active)
                    else:
                        amount = amount * ((1 + annual_change) ** years_active)
                elif event.inflation_adjusted:
                    amount = amount * ((1 + self.inflation_rate) ** years_active)
                # For married couples consider user percentage
                amount *= float(event.user_percentage or 1.0)
                total_income += amount
        self.curYearIncome += total_income
        # Add income to cash (assume cash investment has ID or special handling)
        cash_investment_id = next((inv.id.hex for inv in (self.scenario.investments or []) if inv.name == 'cash'), None)
        if cash_investment_id:
            self.investments[cash_investment_id] = self.investments.get(cash_investment_id, Decimal(0)) + Decimal(total_income)
        print(f"Year {year} income added: {total_income:.2f}")
    
    def _perform_rmd(self, year: int):
        # For simplicity, perform uniform life table RMD calculation (s/d) from investments pre-tax
        pre_tax_investments = [inv for inv in (self.scenario.investments or []) if inv.account_tax_status == AccountTaxStatus.PRE_TAX_RETIREMENT]
        total_pre_tax_value = sum(float(self.investments.get(inv.id.hex, Decimal(0))) for inv in pre_tax_investments)
        if total_pre_tax_value <= 0:
            return
        # Lookup distribution period d from table (stub: use fixed)
        d = 27.4  # e.g., age 74 from IRS uniform life table
        rmd = total_pre_tax_value / d
        self.curYearIncome += rmd
        print(f"Year {year} RMD calculated: {rmd:.2f}")
        # Transfer assets in-kind from pre-tax to non-retirement account according to RMD strategy ordering
        # Simplified: subtract rmd proportionally from investments
        for inv in pre_tax_investments:
            inv_id = inv.id.hex
            val = float(self.investments.get(inv_id, Decimal(0)))
            if val <= 0 or rmd <= 0:
                continue
            transfer_amount = min(val, rmd)
            self.investments[inv_id] = Decimal(val - transfer_amount)
            # Find or create non-retirement investment with same investment type
            non_ret_inv = next((i for i in (self.scenario.investments or []) if i.investment_type_id == inv.investment_type_id and i.account_tax_status == AccountTaxStatus.NON_RETIREMENT), None)
            if non_ret_inv:
                self.investments[non_ret_inv.id.hex] = self.investments.get(non_ret_inv.id.hex, Decimal(0)) + Decimal(transfer_amount)
            else:
                # Ignored for brevity: create new investment
                pass
            rmd -= transfer_amount
            if rmd <= 0:
                break
    
    def _update_investments(self, year: int):
        # Apply annual return, reinvest dividends, subtract expenses according to investment type distributions
        for inv in self.scenario.investments or []:
            inv_id = inv.id.hex
            inv_type = next((t for t in (self.scenario.investment_types or []) if t.id == inv.investment_type_id), None)
            if not inv_type:
                continue
            value = float(self.investments.get(inv_id, Decimal(0)))
            if value <= 0:
                continue
            # Sample expected annual return rate
            annual_return_rate = sample_distribution(inv_type.expected_annual_return, self.rng)
            if inv_type.return_percent:
                delta_value = value * annual_return_rate
            else:
                delta_value = annual_return_rate
            # Sample expected annual income (dividends or interest)
            annual_income = sample_distribution(inv_type.expected_annual_income, self.rng)
            income_value = value * annual_income if inv_type.income_percent else annual_income
            # Expenses based on expense ratio * average of start and end year value (approximate start = value, after delta added end value)
            avg_value = (value + (value + delta_value)) / 2
            expense = avg_value * float(inv_type.expense_ratio)
            # Update investment value
            new_value = value + delta_value + income_value - expense
            new_value = max(new_value, 0.0)  # no negatives
            self.investments[inv_id] = Decimal(new_value)
            # Update curYearIncome if taxable income from dividends (only if non-retirement taxable)
            if inv.account_tax_status == AccountTaxStatus.NON_RETIREMENT and inv_type.taxability == InvestmentTaxability.TAXABLE:
                self.curYearIncome += income_value
            print(f"Year {year} updated investment {inv.name}: value={new_value:.2f}")
    
    def _run_roth_conversion(self, year: int, age: int):
        # Simplified Roth conversion to top off current bracket
        # Lookup current tax bracket upper bound u (stub example)
        u = 40000
        fed_taxable_income = self.curYearIncome - 0.15 * self.curYearSS
        rc_amount = max(0.0, u - (fed_taxable_income - self.standard_deduction))
        if rc_amount <= 0:
            return
        print(f"Year {year} Roth conversion amount: {rc_amount:.2f}")
        # Transfer investments in order (not implemented in detail here)
        # Just add rc_amount to after-tax retirement investments and increase income
        self.curYearIncome += rc_amount
    
    def _pay_expenses(self, year: int, discretionary: bool = False):
        # Sum expenses and pay from cash, withdraw from investments if necessary
        expense_events = [e for e in (self.scenario.event_series or []) if e.type == EventSeriesType.EXPENSE and e.is_discretionary == discretionary]
        total_expense = 0.0
        for event in expense_events:
            # Similar to income calculation but for expense amounts applying changes
            pass  # Implement similarly to _run_income_events
        # Withdraw from cash and other investments per expense withdrawal strategy (not detailed here)
        print(f"Year {year} paid {'discretionary' if discretionary else 'non-discretionary'} expenses: {total_expense:.2f}")
    
    def _run_invest_events(self, year: int):
        # Find invest events active this year, invest excess cash accordingly
        pass  # Implement per project specification
    
    def _run_rebalance_events(self, year: int):
        # Find rebalance events active this year, rebalance investments accordingly
        pass  # Implement per project specification
