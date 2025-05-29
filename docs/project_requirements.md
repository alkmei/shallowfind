### Project Requirements: Lifetime Financial Planner (LFP)

### CSE 416: Software Engineering, Spring 2025

### Professor Scott D. Stoller

### version: 2025-05-0327

# 1 Taxes

Federal taxes. If Federal tax information for the current year is not in the database, the system scrapes the following information and stores it in the database:

1. [Federal income tax rates and brackets](https://www.irs.gov/filing/federal-income-tax-rates-and-brackets) from the linked page
2. standard deductions for most people from [Table 10-1 in IRS Publication 17](https://www.irs.gov/publications/p17)
3. capital gains tax rates and thresholds from [IRS’s capital gains page](https://www.irs.gov/taxtopics/tc409)

State taxes. State income tax rates and brackets are read from a YAML configuration file on the server. This file might lack data for some states. If it lacks data for the user’s state of residence, the system allows the user to upload a YAML file in the same format containing that information. If the user opts not to do this, the system displays a warning message that the financial projections will ignore state income tax.

The system assumes that all tax brackets for future years are adjusted for inflation, i.e., the boundaries increase at the same rate as inflation. Standard deductions are also adjusted for inflation.

Withdrawals from retirement accounts (pre-tax or after-tax) taken before age 59 ½ incur a 10% early withdrawal tax. There are [some exceptions to this rule](https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-exceptions-to-tax-on-early-distributions); for simplicity, the system ignores these exceptions.

Notes. (1) The system computes federal income tax, capital gains tax, early withdrawal tax, and state income tax. The system ignores all other taxes. (2) The system supports only two tax filing statuses: single (if the scenario is for an individual), and married filing jointly (if the scenario is for a married couple). (3) The system assumes users take the federal standard deduction (they do not itemize deductions) and that all income above the standard deduction is taxable at the federal level, aside from the special treatment of social security benefits. (4) The system assumes that the user satisfies the conditions to use the standard deductions in Table 10-1 cited above. (5) The system ignores state income tax on social security benefits, if any. This is reasonable because [most states do not tax social security benefits](https://www.investopedia.com/which-states-dont-tax-social-security-8725930), the details are complicated for some states that do, and state income tax rates are generally small compared to federal income tax rates. If the user receives social security benefits and lives in a state that taxes them, the system displays a warning that this tax is ignored. (6) The system assumes all capital gains are long-term. (7) The system assumes that states tax capital gains the same way as other income. This is reasonable because most states tax them the same way. (8) For simplicity, The system assumes that state income tax can be computed in a similar manner as federal income tax, using a table of tax rates and brackets for each filing status, and ignores any deviations from this. For state income tax, the system also ignores any deductions or exemptions. For example, for NY, it always uses the tax rates and brackets in the “New York State tax rate schedule” in the [Instructions for Form IT-201i](https://www.tax.ny.gov/forms/current-forms/it/it201i.htm) and ignores the other methods mentioned for filers with income below $65000 or above $107,650. (9) For testing and demonstration, it’s sufficient for the YAML configuration file to include state income tax rates and brackets for NY, NJ, and CT. (10) The system assumes that 85% of social security benefits are subject to federal income tax. (11) When part of an investment is sold, use the average cost basis method to compute the capital gains. (12) let Y1 be the earliest year for which the database contains tax data. if you need tax data for a year Y < Y1, simply use the tax data for Y1. (it would probably be better to apply "reverse inflation" to compute estimated tax brackets for earlier years, but you don't need to bother with this.) (13) Cash-like investment options such as savings accts and money market funds typically have zero or negligible capital gains. For simplicity, it's OK to ignore capital gains tax related to the cash investment.

# 2 Scenarios

A _scenario_ is a collection of information defining a user’s financial plan. It can be for an individual or a married couple. It includes: (1) decisions about asset allocation, retirement age, etc., (2) financial goals, and (3) assumptions about expenses, income, major life events, life span, performance of financial markets, etc. It encompasses the information needed to run a set of simulations. It also includes all related settings provided by the user, such as a set of charts used to visualize the results, and sharing information.

## 2.1 Financial goal

A _financial goal_ is a non-negative number specifying the desired minimum total value of the user’s investments. If a financial goal of 0 is achieved, it means the user is always able to meet their expenses. A positive value for the financial goal represents a safety margin during the user’s lifetime and an estate to bequeath afterward.

Notes. Expressing the goal in this way is a simplification, because it ignores loans (e.g., mortgages) and real property (e.g., houses).

## 2.2 Investments

An _investment type_ (also called “asset type”) is defined by

- Name, e.g., “S&P 500” for an S&P 500 index fund, or “municipal bonds"
- description
- expected annual return (change in underlying value), expressed as (1) a fixed amount or percentage, or (2) an amount or percentage sampled from a specified normal distribution. Note that this change is a capital gain or loss. When expressed as a percentage, the percentage is relative to the investment’s value at the beginning of the year.
- expense ratio, a fixed percentage of the value of the investment subtracted annually by the investment provider. The average value of the investment---specifically, the average of its value at the beginning and end of the year---is used to calculate the expenses.
- expected annual income from dividends or interest, expressed in the same possible ways as the expected annual change in value.
- taxability: tax-exempt (such as municipal bonds) or taxable.

An _investment_ is defined by

- investment type
- value (in dollars), the current market value
- tax status of the account it is held in. This can be non-retirement, pre-tax retirement, or after-tax retirement ([Incomewize](https://incomewize.com) calls these taxable, tax-deferred, and tax-free accounts, respectively).

Notes. (1) Dividends and interest are subject to income tax. (2) Tax-exempt investment types should not be held in retirement accounts, because they would not provide any additional tax benefit in that context. (3) The probability distributions should be sampled in each year of a simulation, not just once at the beginning of each simulation.

There is a pre-defined investment type named “cash” that is held in a non-retirement account. the user can enter the other attributes of this investment type (some values are more realistic than others, but the system does not need to enforce any constraints).

## Event series

An _event series_ represents a sequence of annual events. It is defined by

- name
- description (optional)
- start year, expressed as (1) a fixed value, (2) a value selected from a specified uniform or normal distribution, or (3) the same year that a specified event series starts, or (4) the year after a specified event series ends.
- duration, in years, expressed as a fixed value or a value selected from a specified uniform or normal distribution
- type: income, expense, invest, or rebalance
- If type is income or expense, also specify
  - initial amount
  - expected annual change in amount, expressed as (1) a fixed amount or percentage, or (2) an amount or percentage sampled from a specified uniform or normal distribution. Note that the expected annual change should be applied only while the event series is active.
  - Inflation adjustment, a Boolean flag indicating whether the amount increases at the rate of inflation, in addition to the explicitly specified change. Note that inflation-adjustment should be applied even in the years before the event series starts; the "initial amount" is the amount suitable for use in the starting year of the simulation, regardless of when the event series actually starts.
  - If the scenario is for a married couple, also specify the percentage associated with the user.
- If type is income, also specify whether the income is social security (this information is needed to compute federal income tax on social security).
- If type is expense, also specify whether the expense is _discretionary_. If the expense is discretionary, it is incurred in a given year only if that does not lead to a violation of the financial goal in that year.
- If type is invest (representing an investment strategy), also specify
  - an asset allocation among a set of selected investments not in pre-tax accounts. The asset allocation can be expressed as (1) a fixed set of percentages for the selected investments, or (2) a linear [_glide path_](https://smartasset.com/financial-advisor/glide-path), expressed as initial and final sets of percentages. The percentages must sum to 100. With a glide path, the actual percentages used vary linearly between the specified endpoints over the time between the start and end years.
  - maximum cash, the maximum amount to hold, at year’s end, in the pre-defined cash investment. Cash above this amount is called _excess cash_ and is automatically invested in the selected investments.
- If type is rebalance (representing [calendar-based rebalancing](https://smartasset.com/investing/rebalancing-your-portfolio)), also specify an asset allocation among a set of selected investments with the same account tax status. The asset allocation can be expressed in the same ways as for invest events.

Notes. (1) There are no explicit buy events or sell events. Investments are bought when excess income is available, and investments are sold only for a specific purpose, such as paying expenses or rebalancing. (2) Rebalancing may generate capital gains or losses. (3) All income from dividends and interest generated by an investment are automatically reinvested in that investment. (4) Discretionary expenses can be partially incurred, if incurring the entire expense would lead to a violation of the financial goal in the current year. (5) A scenario may not contain temporally overlapping invest event series. (6) A scenario may not contain overlapping rebalance event series for investments with the same account tax status; in other words, for each account tax status, at most one asset allocation for rebalancing can be in effect at a time. (7) Users are responsible for estimating their social security income and including it as an event series.

Examples. (1) Buying a house can be represented with two event series: (a) a downpayment expense series with duration 1 year and a fixed or variable start year (depending on the user’s plans), and (b) a mortgage expense series starting in the same year as the downpayment expense series and with duration 30 years, both with amounts sampled from normal distributions based on the median house price in the user’s area. (2) Having a child can be modeled with two event series: (a) a child-raising expense series, with a start year distributed uniformly in the years when the user is ages 25 and 35, a fixed amount with inflation adjustment, and duration 18 years, and (b) a college expense series with a start year of “after child-raising expense series”, a fixed amount with inflation adjustment, and duration 4 years.

## 2.4 Spending strategy

A _spending strategy_ is an ordering on discretionary expenses. Discretionary expenses are paid one at a time, in the specified order, as long as the financial goal is not violated.

## 2.5 Expense withdrawal strategy

An _expense_ _withdrawal strategy_ is an ordering on a set of investments that specifies the order in which investments are sold to generate cash, if the cash account does not contain sufficient funds to pay expenses and taxes. Investments are sold strictly in that order. In other words, part (possibly all) of an investment is sold only when all investments earlier in the ordering have balance zero. The expense withdrawal strategy can include investments in accounts with any tax status.

it doesn't make sense for non-discretionary expenses and taxes to be unpaid if the user has funds to pay them. The system should either (1) require that the expense withdrawal strategy contain all investments, or, (2) if any investments are omitted, treat them as implicitly appended in some order (your system can determine the order). this includes investments of type pre-tax retirement.

## 2.6 Inflation assumption

An _inflation assumption_ is defined by (1) a fixed percentage, or (2) a percentage sampled from a specified uniform or normal distribution.

## 2.7 Roth conversion optimizer

A _Roth conversion_ is an in-kind transfer of assets from pre-tax retirement accounts to after-tax retirement accounts. Strategically timed Roth conversions can minimize a user’s total (lifetime) income tax; e.g., see discussions at [Investopedia](https://www.investopedia.com/terms/i/iraconversion.asp) and [smartasset](https://smartasset.com/retirement/partial-roth-conversion). The Roth conversion optimizer helps the user determine whether Roth conversions will benefit them.

If the user enables the optimizer for a scenario, the user also specifies a start year and an end year. For each year in that range, the optimizer generates a withdrawal whose amount increases the user’s income to the upper limit of their current federal income tax bracket.

A _Roth conversion strategy_ is an ordering on investments in pre-tax retirement accounts. When a withdrawal is triggered by the optimizer, investments are transferred in-kind, in that order, from pre-tax retirement accounts to after-tax retirement accounts. Part (or all) of an investment is transferred only when all investments earlier in the ordering have balance zero. Note that IRS regulations do not limit the amount of Roth conversions.

## 2.8 RMDs

The system computes required minimum distributions (RMDs) and performs them by transferring assets in-kind from investments in pre-tax retirement accounts to investments in non-retirement accounts. Note that “distribution” here is synonymous with “withdrawal”. RMDs are specified by [IRS Publication 590-B Distributions from Individual Retirement Arrangements (IRAs)](https://www.irs.gov/publications/p590b). See, e.g., [smartasset’s RMD page](https://smartasset.com/retirement/rmd-table) for an easier-to-read introduction to RMDs, and the [IRS’s RMD FAQ](https://www.irs.gov/retirement-plans/retirement-plan-and-ira-required-minimum-distributions-faqs).

The system does not initially know any RMD tables. If the RMD table for the current year is not in the database, the system scrapes Table III (Uniform Life Table) from [IRS Publication 590-B](https://www.irs.gov/publications/p590b) and stores it in the database. Since most people satisfy the conditions for using Table III, for simplicity, the system assumes the user satisfies those conditions. When computing RMDs for future years, use the current year's RMD table.

An _RMD_ _strategy_ is an ordering on investments in pre-tax retirement accounts. When a withdrawal is triggered by a RMD, investments are transferred in-kind, in that order, from pre-tax retirement accounts to non-retirement accounts. Part (or all) of an investment is transferred only when all investments earlier in the ordering have balance zero.

Note. For simplicity, the system does not support directly investing an RMD in an after-tax retirement account, i.e., using it for a Roth conversion. If the user wants to perform Roth conversions, they should enable the Roth conversion optimizer. The simulator processes Roth conversions before RMDs; this voluntary distribution from pre-tax retirement accounts potentially preempts the need for a RMD.

## 2.9 Scenarios

A scenario is defined by:

1. name
2. whether the scenario is for an individual or married couple
3. birth year of the user and the spouse if any
4. life expectancy of the user and the spouse if any, expressed as a fixed age or an age sampled from a normal distribution (although [the actual distribution is asymmetric](https://www.ssa.gov/policy/docs/rsnotes/rsn2016-02.html))
5. set of investment types, and a set of investments with their current values
6. set of event series
7. inflation assumption
8. initial limit on annual contributions to after-tax retirement accounts. The limit is imposed by the IRS. It is inflation-adjusted, i.e., assumed to increase annually at the rate of inflation.
9. spending strategy, expense withdrawal strategy, RMD strategy, and Roth conversion strategy
10. Roth conversion optimizer settings
11. sharing settings (see Section 7.1)
12. financial goal
13. user’s state of residence

Notes. (1) For simplicity, assume the IRS annual contribution limits for retirement accounts adjust smoothly with inflation, even though they actually adjust in $500 increments. (2) For simplicity, assume that investments have no capital gains at the start of the simulation.

# 3 Simulation

A simulation of a scenario starts in the current year and ends when the user reaches their life expectancy (“dies”). For each year, the algorithm performs the following steps:

1. Run income events, adding the income to the cash investment.
2. Perform the RMD for the previous year, if any.
3. Update the values of investments, including annual return, subtraction of expenses, and reinvestment of dividends and interest.
4. Run the Roth conversion optimizer, if it is enabled.
5. Pay non-discretionary expenses and the previous year’s taxes, i.e., subtract them from the cash investment. Perform additional withdrawals if needed to pay them.
6. Pay discretionary expenses if that does not lead to a violation of the financial goal.. Perform additional withdrawals if needed to pay them.
7. Run the invest event scheduled for the current year, if any, by using excess cash to buy investments included in the specified asset allocation, apportioning the excess cash according to that asset allocation, while taking inflation-adjusted annual limits on retirement account contributions into account.
8. Run rebalance events scheduled for the current year, by selling and buying the investments included in the specified asset allocation to achieve the specified ratios between their values.

Notes. (1) For married couples, the system assumes that all investments are jointly owned, and the beneficiary is the surviving spouse. When the user or the spouse reaches their life expectancy (“dies”), the percentages of income and expense transactions associated with the deceased spouse are omitted from transaction amounts for future years, and the survivor’s tax filing status changes from married filing jointly to single. (2) For simplicity, the system assumes that no tax needs to be paid in the starting year of the simulation. (3) For simplicity, all simulations start in the current actual year.

# 4 Charts

After defining a scenario, the user specifies how many simulations to perform and runs them..

The user then selects a set of charts to be generated to visualize the results. The set may include multiple charts of the same kind, e.g., multiple shaded line charts. For all charts, hovering over an appropriate visual element---point, shaded region, bar, etc., depending on the chart type---raises a pop-up displaying associated numerical values. Charts that show values of investments over time (e.g., charts 4.2.1 and 5.1.2) should show the values of the investments at the end of each year.

## 4.1 Line chart of probability of success over time

This line chart shows the probability of success over time. For a given year, this is the percentage of simulations in which the financial goal is satisfied in that year. To determine whether the financial goal is satisfied in a given year, it is sufficient to check the total value of investments at the end of the year. Note that [a success probability less than 100% might be OK](https://www.linkedin.com/pulse/goldilocks-just-right-probability-retirement-planning-cordaro/).

## 4.2 Shaded line chart of probability ranges for a selected quantity over time

This type of line chart includes a line for the median value of a selected quantity over time (i.e., year by year), with shaded regions depicting probability ranges---specifically 10%-90%, 20%-80%, 30%-70%, and 40%-60%---for the value of that quantity. The selected quantity may be

1. total investments (the chart should also include a horizontal line representing the financial goal)
2. total income
3. total expenses, including taxes
4. early withdrawal tax
5. percentage of total discretionary expenses incurred (the percentage is based on the amounts, not the number, of the discretionary expenses in that year).

## 4.3 Stacked bar chart of median or average values of a selected quantity over time

A stacked bar chart with a bar for each year, and with each bar segmented to show

1. a breakdown of total investments by investment (If possible, visually indicate the tax status of the account containing the investment, and use adjacent segments for investments with the same tax status.), or
2. a breakdown of income by event series (note that income generated by investments is not associated with an event series hence is not included in this chart), or
3. a breakdown of expenses by event series, plus a segment for taxes

The user selects whether to use median or average values. For example, if the user selects average values for the investments chart, the height of each segment of the bar for year Y is the average value (across the set of simulations) in year _Y_ of one of the investments. To avoid clutter, the user can specify an aggregation threshold. Categories whose values are below that threshold in every year of every simulation are aggregated and displayed as a single “Other” category. Hovering over a bar raises a pop-up displaying the height of the bar and the height of each segment.

# 5 One-dimensional scenario exploration

A \_scenario paramete_r is (a) the Boolean flag for enabling the Roth optimizer, or (b) one of the following scenario settings:

1. start year or duration of an event series
2. initial amount of an income or expense event series, or
3. the percentage associated with the first investment in an asset allocation in an invest event series whose asset allocation is among exactly two selected investments. The percentage associated with the second investment is automatically chosen so that the two percentages sum to 100.

For example, a user can explore different retirement ages by making the duration of the “salary” event series a scenario parameter.

The user can specify one scenario parameter and, if it is numeric, a set of values for it, defined by a lower bound, an upper bound, and a step size. The system performs a set of simulations for each value of the parameter. The system re-seeds the pseudo-random number generator (PRNG) to ensure that it starts from the same seed for each set of simulations. After the simulations, the user can view the following charts. The user can also view (in the ways described in Section 4) the results for a selected parameter value.

Notes. You may add a restriction that Roth conversion optimization (RCO) can be selected as a parameter for a given scenario only if RCO is enabled in the given scenario; this ensures that the user has already specified the start and end years. It's also fine to avoid this restriction by allowing the user to specify the starting and ending years when they select RCO as a parameter for a scenario in which RCO was disabled. the starting and ending years are not really additional parameters, because the exploration considers only a single value for each of them.

## 5.1 Multi-line chart of the value of a selected quantity over time

The chart contains a line for each value of the parameter. The selected quantity may be

1. probability of success
2. median total investments

## 5.2 Line chart of a selected quantity as a function of parameter value

This type of chart is applicable if the scenario parameter is numeric. The selected quantity may be

1. final value of probability of success
2. final value of median total investments

# 6 Two-dimensional scenario exploration

This is similar to one-dimensional exploration, except that the user specifies two numeric scenario parameters, and the system performs a set of simulations for each combination of their values. The following charts are available, in addition to viewing (in the ways described in Section 4) the results for a selected combination of parameter values.

6.1 [Surface plot](https://en.wikipedia.org/wiki/Plot_%28graphics%29#Surface_plot) of a selected quantity as a function of parameter values

The available quantities are the same as for the line charts in Section 5.2.

6.2 Contour plot of a selected quantity as a function of parameter values

The available quantities are the same as for the line charts in Section 5.2.

# 7 Other requirements

7.1 Authentication, user profiles, and sharing. The system can be used anonymously (i.e., without login), or as an authenticated user by logging in with a Google account. An authenticated user can save scenarios on the server and revisit them later. YAML files with state tax rates and brackets uploaded by a user are also saved in the user’s profile. An authenticated user can give other authenticated users, such as a spouse or financial advisor, read-only or read-write access to specific scenarios.

7.2 Import and export. Users can export (download) the current scenario as a YAML file and can import (upload) these files. The required format is defined by scenario.yaml posted in Google Classroom

7.3 Parallelism. The system runs multiple simulations in parallel to reduce end-to-end analysis time. Note that creating processes is relatively expensive, so parallelism should be implemented using (or re-using) multiple threads in a single process (for example, using [worker threads](https://nodejs.org/api/worker_threads.html) in Node.js) or by re-using processes in a pool of worker processes.

7.4 Usability. The system provides an easy-to-use, user-friendly web interface consistent with established UI design principles. The system handles invalid inputs gracefully and provides informative error messages. The system displays help text to guide users. _All assumptions, limitations, and simplifications used in the calculations (including those mentioned in this document) are documented in explanatory text._

7.5 Logs. To facilitate debugging (and grading), the system logs detailed information about the first simulation in each set of simulations executed. Specifically, in a log folder on the server, it creates two files. One is named \_user*\_\_datetime*.csv, where _user_ is the name of the user who ran the simulations and _datetime_ is the current datetime. It contains a title row and a row for each year in the simulation. It contains a column for the year and a column for each investment showing the value of that investment at the end of the year. The second file is named _user_datetime_.log, in any easily human-readable format. It contains an entry for every financial event. A financial event is described by the year, transaction type (income, Roth conversion, RMD, expense, tax, invest, or rebalance), amount(s), and other details (e.g., the name of the income event series, the investment moved in a Roth conversion, the type of tax paid, or the investments sold and purchased in a rebalance).

7.6 Deployment. The system is usable by end users running only a web browser on their computer. Deployment on a server eliminates the need for users to install software and supports scenario sharing.

# Advice

If you decide to open-source your system after the end of the semester, add a disclaimer that anyone who makes decisions based on the output of your system does so at their own risk.

# Background information

tax-exempt investments:

- always held in non-retirement accounts (as stated in section 2.2., note 2).
- generated income is exempt from federal income tax and sometimes also from state income tax. for simplicity, assume the income is exempt from both.
- capital gains from selling the investment are subject to capital gains tax.
- much info is available on the web, e.g., <https://www.investopedia.com/ask/answers/060215/how-are-municipal-bonds-taxed.asp>

investments in accounts with tax status = after-tax retirement:

- these are usually called "Roth accounts" or "Roth retirement accounts".
- interest and capital gains from investments in these accounts are not subject to tax, ever (not in the year they were earned, not when they are withdrawn, never).

investments in accounts with tax status = pre-tax retirement:

- as explained in my March 10 posting "no contributions to pre-tax retirement accounts", in LFP, users cannot add new money to pre-tax retirement accounts.
- all withdrawals from investments in these accounts are subject to income tax, regardless of whether the withdrawn funds are capital (i.e., the originally invested money), interest, or capital gains.
