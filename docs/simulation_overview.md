# Simulation Algorithm Overview

CSE 416: Software Engineering, Spring 2025

Professor Scott D. Stoller

version: 2025-04-14

Here is an overview of the algorithm for processing a single year. In the description, “current year” means the current simulated year, not the current actual year. The main loop over years is not shown. Scraping of tax-related data is not shown, since it can be done before the main loop. This overview is intended to be helpful but does not come with a guarantee that all aspects of the calculations are mentioned.

1. **Preliminaries**

   1. If the inflation assumption uses a probability distribution, sample from that distribution and store the result as the current year's inflation rate, for use in all inflation-related calculations for the year. It’s simplest to do this before processing any events, so this value is available whenever it is first needed.
   2. Compute and store inflation-adjusted tax brackets for the current year. This needs to be done by saving the tax brackets each year, and updating the previous year’s tax brackets using the current year’s inflation rate. A formula like initAmount \* (1 + inflation)^(#years) cannot be used when the inflation rate can be selected from a probability distribution. Using such a formula is also slower.
   3. Compute and store the inflation-adjusted annual limits on retirement account contributions, in a similar way.

2. **Run income events, adding the income to the cash investment.**

   1. The amount of this income event in the previous year needs to be stored and updated based on the expected annual change in amount, because the expected annual change can be sampled from a probability distribution, and the sampling is done each year.
   2. If the inflation-adjustment flag is set, adjust the amount for inflation.
   3. If user or their spouse is dead, omit their percentage of the amount.
   4. Add the income to the cash investment.
   5. Update running total curYearIncome
   6. Update running total curYearSS of social security benefits, if income type = social security.

3. **Perform the RMD for the previous year, if the user’s age is at least 74 and at the end of the previous year, there is at least one investment with tax status = “pre-tax” and with a positive value.**

   1. The first RMD is for the year in which the user turns 73, and is paid in the year in which the user turns 74.
   2. Distribution period d = result from lookup of the user’s age in the most recent available RMD table (typically the current actual year’s RMD table).
   3. s = sum of values of the investments with tax status = pre-tax, as of the end of the previous year. (don’t look for “IRA” in the name of the investment type. employer-sponsored pre-tax retirement accounts are not IRAs.)
   4. rmd = s / d
   5. curYearIncome += rmd
   6. Iterate over the investments in the RMD strategy in the given order, transferring each of them in-kind to an investment with the same investment type and with tax status = “non-retirement”, until the total amount transferred equals rmd. The last investment to be transferred might be partially transferred.
   7. “Transferring in-kind” means reducing the value of the source investment by the transferred amount, checking whether an investment with the same investment type and target tax status already exists, and if so, adding the transferred amount to its value, otherwise creating an investment with the same investment type, the target tax status, and value equal to the transferred amount.

4. **Update the values of investments, reflecting expected annual return, reinvestment of generated income, and subtraction of expenses.**

   1. Calculate the generated income, using the given fixed amount or percentage, or sampling from the specified probability distribution.
   2. Add the income to curYearIncome, if the investment’s tax status is ‘non-retirement’ and the investment type’s taxability is ‘taxable’. (For investments in pre-tax retirement accounts, the income is taxable in the year it is withdrawn from the account. For investments in after-tax retirement accounts, the income is not taxable.)
   3. Add the income to the value of the investment. **_Note:_** _Steps 3.c and 3.d should be swapped._
   4. Calculate the change in value, using the given fixed amount or percentage, or sampling from the specified probability distribution.
   5. Calculate this year’s expenses, by multiplying the expense ratio and the average value of the investment (i.e., the average of its value at the beginning and end of the year). Subtract the expenses from the value.

5. **Run the Roth conversion (RC) optimizer, if it is enabled.**

   1. Look up curYearFedTaxableIncome in the inflation-adjusted federal income tax brackets for the current year, to find the user’s current federal income tax bracket, where curYearFedTaxableIncome = curYearIncome – 0.15\*curYearSS. u = the upper limit of that bracket.
   2. Amount of Roth conversion rc = u – (curYearFedTaxableIncome - standardDeduction)
   3. Iterate over the investments in the Roth conversion strategy in the given order, transferring each of them in-kind to an investment with the same investment type and with tax status = “after-tax retirement”, until the total amount transferred equals rc. The last investment to be transferred might be partially transferred.
   4. curYearIncome += rc.
   5.

6. **Pay non-discretionary expenses and the previous year’s taxes, i.e., subtract them from the cash investment. Perform additional withdrawals if needed to pay them.**

   1. Calculate the previous year’s federal and state income tax using the values of curYearIncome and curYearSS from the previous year, and inflation-adjusted federal and state income tax data (rates, brackets, and standard deduction) for the previous year.
   2. Calculate the previous year’s capital gains tax using the value of curYearGains from the previous year, and inflation-adjusted federal capital gains tax data for the previous year. I recommend [SmartAsset’s article on capital gains tax](https://smartasset.com/investing/capital-gains-tax-definition). Note that capital gains tax cannot be negative, even if the user has a net loss. The IRS allows carrying capital losses forward to future years; we ignore this.
   3. Calculate the previous year’s early withdrawal tax, using the value of curYearEarlyWithdrawals from the previous year.
   4. total payment amount P = sum of non-discretionary expenses in the current year plus the previous year’s taxes. Calculate the amounts of expense events in a similar way as calculating the amounts of income events.
   5. total withdrawal amount W = P - (amount of cash)
   6. Iterate over investments in the expense withdrawal strategy, selling them one by one, until the total amount sold equals W. The last investment to be sold might be partially sold.
      1. For each sale, compute the capital gain, and update running total curYearGains of capital gains, if the sold investment’s tax status is “non-retirement”. If the entire investment is sold, capital gain = current value - purchase price, where purchase price = sum of the amounts of purchases of this investment plus the initial value at the start of the simulation. Note that the purchase price must be stored, and updated upon each purchase. If a fraction f of an investment is sold, then capital gain = f \* (current value - purchase price). Update the purchase price in a similar way: purchase price = (1 - f) \* purchase price.
      2. Note that the capital “gain” may be negative (i.e., a loss), and that capital gains tax is paid on the net capital gain for the year. Note that capital gains in pre-tax retirement accounts are taxed as regular income upon withdrawal from the pre-tax retirement account.
      3. Update running total curYearIncome, if the investment sold is held in a pre-tax retirement account. This reflects that we are both selling the investment and withdrawing the funds from the pre-tax retirement account in order to pay the expense.
      4. Update running total curYearEarlyWithdrawals, if the investment sold is held in a pre-tax or after-tax retirement account and the user’s age is less than 59. If the user’s age equals 59, we assume they perform this withdrawal after they turn 59½.

7. **Pay discretionary expenses in the order given by the spending strategy, except stop if continuing would reduce the user’s total assets below the financial goal. The last discretionary expense to be paid can be partially paid, if incurring the entire expense would violate the financial goal. Perform additional withdrawals if needed to pay them.**

   1. Details are similar to the details of paying non-discretionary expenses.

8. **Run the invest event scheduled for the current year, if any, by using excess cash to buy investments included in the asset allocation in the invest event, apportioning the excess cash according to that asset allocation.**

   1. Take the inflation-adjusted annual limit L on after-tax retirement account contributions into account as follows. calculate B = sum of the amounts to buy of investments with tax status = “after-tax retirement”. If B > L, then uniformly scale down the purchases of after-tax investments by L/B, and uniformly scale up the purchases of non-retirement investments, so that the grand total still equals the amount of excess cash. Note that Roth conversions from pre-tax retirement accounts to after-tax retirement accounts do not count toward the annual contribution limit for after-tax retirement accounts.
   2.

9. **Run rebalance events scheduled for the current year, by selling and buying the investments included in the specified asset allocation to achieve the specified ratios between their values.**
   1. Compute the target value of each investment, and then adjust its amount by buying or selling, as appropriate. For each sale of an investment whose tax status is “non-retirement”, calculate the capital gains on the sale and update curYearGains. In principle, I would first process all of the sales, and then all of the purchases. In practice, the processing order doesn’t affect the outcome.
