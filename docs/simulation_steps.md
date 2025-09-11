# Lifetime Financial Planner - Simulation Algorithm Outline

## State Variables to Track Throughout Simulation

### Annual Running Totals (reset each year)

- `curYearIncome` - Total income for current year
- `curYearSS` - Social security benefits for current year
- `curYearGains` - Capital gains/losses for current year
- `curYearEarlyWithdrawals` - Early withdrawal amount for current year

### Investment Tracking

- For each investment: `currentValue`, `purchasePrice` (cost basis)
- Cash investment amount
- Investment values by tax status (non-retirement, pre-tax retirement, after-tax retirement)

### Tax Data (inflation-adjusted annually)

- Federal tax brackets and rates
- State tax brackets and rates
- Standard deductions
- Capital gains tax rates and thresholds
- Annual contribution limits for retirement accounts

### Event Series State

- Previous year amounts for each income/expense event series
- Active event series for current year
- Start/end years for each event series

### User State

- Current age of user and spouse
- Tax filing status (single/married filing jointly)
- Whether user/spouse is deceased

## Annual Simulation Algorithm

### Step 1: Preliminaries

```
1.1 Sample inflation rate for current year
    if inflation_assumption.type == "distribution":
        current_inflation = sample(inflation_assumption.distribution)
    else:
        current_inflation = inflation_assumption.fixed_rate

1.2 Update tax brackets for inflation
    for each tax bracket:
        bracket.lower_bound *= (1 + current_inflation)
        bracket.upper_bound *= (1 + current_inflation)

    standard_deduction *= (1 + current_inflation)

1.3 Update retirement contribution limits
    annual_contribution_limit *= (1 + current_inflation)

1.4 Initialize annual totals
    curYearIncome = 0
    curYearSS = 0
    curYearGains = 0
    curYearEarlyWithdrawals = 0
```

### Step 2: Process Income Events

```
2.1 For each active income event series:

    2.2 Update amount from previous year
        if expected_annual_change.type == "distribution":
            change = sample(expected_annual_change.distribution)
        else:
            change = expected_annual_change.value

        if expected_annual_change.is_percentage:
            new_amount = previous_amount * (1 + change)
        else:
            new_amount = previous_amount + change

    2.3 Apply inflation adjustment
        if inflation_adjustment == true:
            new_amount *= (1 + current_inflation)

    2.4 Apply spouse percentage if applicable
        if user_deceased:
            new_amount *= (1 - user_percentage)
        if spouse_deceased:
            new_amount *= user_percentage

    2.5 Add to cash and running totals
        cash_investment.value += new_amount
        curYearIncome += new_amount

        if event_series.is_social_security:
            curYearSS += new_amount

    2.6 Store amount for next year
        event_series.previous_amount = new_amount
```

### Step 3: Process Required Minimum Distributions (RMDs)

```
3.1 Check RMD eligibility
    if user_age >= 74 AND sum(pre_tax_investments.values) > 0:

    3.2 Calculate RMD amount
        distribution_period = lookup_rmd_table(user_age)
        pre_tax_total = sum(pre_tax_investments.end_of_previous_year_values)
        rmd_amount = pre_tax_total / distribution_period

    3.3 Transfer investments in-kind
        remaining_to_transfer = rmd_amount
        for investment in rmd_strategy.order:
            if remaining_to_transfer <= 0: break

            transfer_amount = min(investment.value, remaining_to_transfer)

            # Transfer in-kind to non-retirement account
            investment.value -= transfer_amount
            find_or_create_non_retirement_investment(investment.type).value += transfer_amount

            remaining_to_transfer -= transfer_amount

    3.4 Update income total
        curYearIncome += rmd_amount
```

### Step 4: Update Investment Values

```
4.1 For each investment:

    4.2 Calculate generated income (dividends/interest)
        if investment_type.income.type == "distribution":
            income = sample(investment_type.income.distribution)
        else:
            income = investment_type.income.value

        if investment_type.income.is_percentage:
            generated_income = investment.value * income
        else:
            generated_income = income

    4.3 Add income to taxable income if applicable
        if investment.tax_status == "non-retirement" AND investment_type.taxability == "taxable":
            curYearIncome += generated_income

    4.4 Reinvest income
        investment.value += generated_income

    4.5 Calculate value change (capital gains/losses)
        if investment_type.return.type == "distribution":
            return_rate = sample(investment_type.return.distribution)
        else:
            return_rate = investment_type.return.value

        if investment_type.return.is_percentage:
            value_change = investment.value * return_rate
        else:
            value_change = return_rate

        investment.value += value_change

    4.6 Subtract expense ratio
        average_value = (beginning_value + investment.value) / 2
        expenses = average_value * investment_type.expense_ratio
        investment.value -= expenses
```

### Step 5: Roth Conversion Optimizer

```
5.1 If Roth conversion optimizer enabled and current_year in [start_year, end_year]:

    5.2 Calculate current tax bracket
        fed_taxable_income = curYearIncome - 0.15 * curYearSS - standard_deduction
        current_bracket = find_tax_bracket(fed_taxable_income)
        bracket_upper_limit = current_bracket.upper_bound

    5.3 Calculate conversion amount
        rc_amount = bracket_upper_limit - fed_taxable_income

    5.4 Transfer investments in-kind
        remaining_to_convert = rc_amount
        for investment in roth_conversion_strategy.order:
            if remaining_to_convert <= 0: break

            convert_amount = min(investment.value, remaining_to_convert)

            # Transfer in-kind to after-tax retirement account
            investment.value -= convert_amount
            find_or_create_after_tax_investment(investment.type).value += convert_amount

            remaining_to_convert -= convert_amount

    5.5 Update income total
        curYearIncome += rc_amount
```

### Step 6: Pay Non-Discretionary Expenses and Taxes

```
6.1 Calculate previous year's taxes

    6.2 Federal income tax
        prev_fed_taxable = prevYearIncome - 0.85 * prevYearSS - prev_standard_deduction
        fed_income_tax = calculate_progressive_tax(prev_fed_taxable, fed_tax_brackets)

    6.3 State income tax
        state_income_tax = calculate_progressive_tax(prevYearIncome, state_tax_brackets)

    6.4 Capital gains tax
        capital_gains_tax = max(0, calculate_capital_gains_tax(prevYearGains))

    6.5 Early withdrawal tax
        early_withdrawal_tax = prevYearEarlyWithdrawals * 0.10

    6.6 Calculate non-discretionary expenses
        total_expenses = 0
        for each non_discretionary_expense_event:
            # Update amount similar to income events (Step 2.2-2.4)
            total_expenses += updated_amount

    6.7 Calculate total payment needed
        total_payment = total_expenses + fed_income_tax + state_income_tax +
                       capital_gains_tax + early_withdrawal_tax

    6.8 Withdraw funds if cash insufficient
        withdrawal_needed = total_payment - cash_investment.value

        if withdrawal_needed > 0:
            perform_withdrawals(withdrawal_needed, expense_withdrawal_strategy)
```

### Step 7: Pay Discretionary Expenses

```
7.1 For each discretionary expense in spending_strategy.order:

    7.2 Calculate expense amount (similar to Step 6.6)

    7.3 Check financial goal constraint
        projected_total_assets = sum(all_investment_values) - expense_amount

        if projected_total_assets >= financial_goal:
            # Pay full expense
            payment_amount = expense_amount
        else:
            # Pay partial expense or skip
            payment_amount = max(0, sum(all_investment_values) - financial_goal)

    7.4 Withdraw funds if needed
        if payment_amount > cash_investment.value:
            withdrawal_needed = payment_amount - cash_investment.value
            perform_withdrawals(withdrawal_needed, expense_withdrawal_strategy)

        cash_investment.value -= payment_amount
```

### Step 8: Process Investment Events

```
8.1 If invest event scheduled for current year:

    8.2 Calculate excess cash
        excess_cash = cash_investment.value - maximum_cash_limit

    8.3 Apply asset allocation
        for each investment in asset_allocation:
            allocation_amount = excess_cash * investment.percentage

            # Check retirement account contribution limits
            if investment.tax_status == "after-tax retirement":
                after_tax_total += allocation_amount

        # Scale down after-tax investments if over limit
        if after_tax_total > annual_contribution_limit:
            scale_factor = annual_contribution_limit / after_tax_total
            # Redistribute excess to non-retirement investments

    8.4 Purchase investments
        for each investment in allocation:
            find_or_create_investment(investment.type, investment.tax_status).value += final_amount
            update_purchase_price(investment, final_amount)

        cash_investment.value -= excess_cash
```

### Step 9: Process Rebalancing Events

```
9.1 If rebalance event scheduled for current year:

    9.2 Calculate target values
        total_value = sum(investments_in_rebalance_scope.values)

        for each investment in asset_allocation:
            target_value = total_value * investment.percentage
            current_value = investment.current_value
            adjustment_needed = target_value - current_value

    9.3 Process sales first
        for each investment where adjustment_needed < 0:
            sale_amount = abs(adjustment_needed)

            # Calculate capital gains if non-retirement account
            if investment.tax_status == "non-retirement":
                capital_gain = calculate_capital_gain(investment, sale_amount)
                curYearGains += capital_gain

            investment.value -= sale_amount
            cash_available += sale_amount

    9.4 Process purchases
        for each investment where adjustment_needed > 0:
            purchase_amount = min(adjustment_needed, cash_available)
            investment.value += purchase_amount
            update_purchase_price(investment, purchase_amount)
            cash_available -= purchase_amount
```

## Helper Functions

### Withdrawal Processing

```
perform_withdrawals(amount_needed, withdrawal_strategy):
    remaining_needed = amount_needed

    for investment in withdrawal_strategy.order:
        if remaining_needed <= 0: break

        withdrawal_amount = min(investment.value, remaining_needed)

        # Calculate capital gains for non-retirement accounts
        if investment.tax_status == "non-retirement":
            capital_gain = calculate_capital_gain(investment, withdrawal_amount)
            curYearGains += capital_gain

        # Add to taxable income for pre-tax retirement withdrawals
        if investment.tax_status == "pre-tax retirement":
            curYearIncome += withdrawal_amount

        # Track early withdrawals
        if user_age < 59 AND investment.tax_status in ["pre-tax retirement", "after-tax retirement"]:
            curYearEarlyWithdrawals += withdrawal_amount

        investment.value -= withdrawal_amount
        cash_investment.value += withdrawal_amount
        remaining_needed -= withdrawal_amount
```

### Capital Gains Calculation

```
calculate_capital_gain(investment, sale_amount):
    if sale_amount >= investment.value:
        # Selling entire investment
        capital_gain = investment.value - investment.purchase_price
        investment.purchase_price = 0
    else:
        # Partial sale using average cost basis
        fraction_sold = sale_amount / investment.value
        capital_gain = fraction_sold * (investment.value - investment.purchase_price)
        investment.purchase_price *= (1 - fraction_sold)

    return capital_gain
```

### Tax Calculations

```
calculate_progressive_tax(taxable_income, tax_brackets):
    total_tax = 0
    remaining_income = taxable_income

    for bracket in tax_brackets:
        if remaining_income <= 0: break

        bracket_income = min(remaining_income, bracket.upper_bound - bracket.lower_bound)
        bracket_tax = bracket_income * bracket.rate
        total_tax += bracket_tax
        remaining_income -= bracket_income

    return total_tax
```

## End-of-Year Processing

```
1. Store investment values for RMD calculations next year
2. Save previous year totals (curYearIncome, curYearSS, curYearGains, curYearEarlyWithdrawals)
3. Check if financial goal is met: sum(all_investment_values) >= financial_goal
4. Update user/spouse ages
5. Check if user/spouse has reached life expectancy
6. Log detailed transaction information if this is the first simulation
```

## Key Formulas Summary

- **Inflation Adjustment**: `amount *= (1 + inflation_rate)^years`
- **RMD Amount**: `sum(pre_tax_values_end_of_prev_year) / distribution_period`
- **Federal Taxable Income**: `income - 0.85 * social_security - standard_deduction`
- **Capital Gains**: `sale_proceeds - cost_basis`
- **Early Withdrawal Penalty**: `withdrawal_amount * 0.10`
- **Investment Return**: `value * return_rate` (if percentage) or `fixed_amount`
- **Expense Ratio**: `average_investment_value * expense_ratio`
