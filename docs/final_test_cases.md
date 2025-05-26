CSE416: Software Engineering, Spring 2025

Scott Stoller

**hw9-code3 test cases for demo**

version: 2025-05-09

anything that cannot be verified by viewing a chart (because the chart is missing or broken) should be verified by viewing a log.

To check correctness of taxes paid, my instructions say to look at the log, because the stacked bar chart of expenses+tax is not required to show the breakdown of different kinds of tax. Some teams show the tax breakdown in the chart anyway, which is good! For those teams, save time by looking at the chart instead of the log.

When a team finishes running our test cases, ask them to put the log files (.csv and .log) generated during the demo in a zip file and upload it to google classroom under the assignment ‘hw9 demo logs’.

I created yaml files for most of these tests. You are welcome to share these files with teams during their demos (share the file using the file icon at the bottom of the Zoom chat window, or send it by email). the name of the yaml file indicates which test it is for However, teams should create the scenarios using their UI for create/edit scenarios, to test the UI, except where noted below.

# Setup

**Action:** login to the system with a google account. Call it U1. all actions below are by U1 unless specified otherwise.

# investment test

**Action:** add the following scenario.

**General info**

Name: investment

user birth year 2025

life expectancy 10 years

marital status: single

Inflation 0

Roth conversion optimization: off

financial goal 2000

Residence state: AK (or any state without tax data in the DB, or with no state income tax)

After-tax retirement account contribution limit: 7000

**investment type: cash**

Annual return: 0

income 0

Taxability: taxable

Expense ratio 0%

**investment type: it1** (“it1” is the name. the same format is used below.)

Description: d1

annual return: amount, normal distrib, mean 200, stdev 40

Expense ratio 0%

Annual income: percentage, normal distrib, mean 10%, stdev 3%

taxability: taxable

**investment type: it2**

Description: d2

annual return: 0

Annual Income: amount, fixed, 2

Expense ratio 1%

taxability : taxable

**Investment cash**

Type cash

Value 100

ax status: non-retirement

**investment i1**

type it1

tax status: pre-tax retirement

value 1000

**investment i2**

type it2

tax status: pre-tax retirement

value 100

**RMD strategy:** \[i2, i1\]

**Grading:** check:

1. the above info can be entered.
2. When entering ‘residence state: AK“ (or suitable replacement), the system warns that state tax data is unavailable, and state income tax will be ignored in sims. It’s OK if this warning is instead displayed when the user prepares to run (or after they run) a sim.
3. When entering an investment type’s annual return, the UI gives
   1. a choice of amount or percentage, and
   2. a choice of fixed value, uniform distribution, or normal distribution.
4. When entering an investment type’s income, the UI gives
   1. a choice of amount or percentage, and
   2. a choice of fixed value, uniform distribution, or normal distribution.
5. For the built-in “cash” investment type, all attributes other than the name are editable.

**Action:** run 50 sims.

**Grading:** check:

1. Shaded line chart of total investments over time shows that the median starts at $1200 and increases by roughly $300/yr.
2. The same chart contains shaded regions depicting the percentile ranges 10%-90%, 20%-80%, 30%-70%, and 40%-60%. (See the project requirements for an example.)
3. shaded line chart of income over time shows that total income varies each year, with a median of about $100 and std deviation of about $30 in the earlier years (will be larger later due to compounding effect). This line chart should also contain shaded regions depicting those percentile ranges.
4. stacked bar chart of investments shows that the value of investment i1 increases by roughly $300/yr on average ($200 from the annual return and $100 from the re-invested income)..
5. stacked bar chart of investments shows that the value of investment i2 increases by about $1 each year (add $2 income, subtract $1 expenses).
6. line chart of probability of success over time shows that the probability of success is roughly 0% in the first 2 or 3 years, and climbs to roughly 100% by the 3rd or 4th year. **Explanation:** Total assets starts at $1200 and increase by an avg of about $300/yr, so it exceeds $2000 after roughly $800 / ($300/yr) = 2.5 years..

# Export test

**Action:** Export the above scenario.

**Action:** view the downloaded file.

**Grading:** quickly check that the format looks correct. If you have doubts, ask the team to include the file in the zip file with logs that they upload to google classroom after the demo, and make a note to yourself to look at it more carefully after the demo.

# parallelism test

**Action:** open a CPU usage monitor: on Windows, open Task Manager; on macOS or Linux, run ‘top’ in a terminal window.

**Action:** Run enough simulations that the set of simulations will take roughly 30 seconds. Ask the team for guidance and/or base it on how long the above 50 simulations took .

**Grading:** record the CPU utilization. For full credit, it should be at least (say) 80%.

# sharing test

#

**Action:** Share the above scenario read-only with another google account. Call that account U2.

**Grading:** check that the UI shows that the scenario has been shared with U2.

**Action by U2:** in a browser window with independent cookie storage \[see hw9-code3 grading guide for details\], login as U2.

View and attempt to edit the scenario.

**Grading:** check that U2 can view and cannot edit the scenario.

**Action:** change the sharing with U2 from read-only to read/write. (It’s OK if this is done by unsharing and then re-sharing the scenario.)

**Action by U2:** change the scenario name to expense1

**Action:** refresh the page and view the scenario name.

**Grading:** Check that U1 sees the updated scenario name.

# RMD test

**Action:** edit the above scenario as follows.

change the annual return and annual income to 0, for both investment types.  
Change the user’s birth year to 1955.

Change the user’s life expectancy to 75.

Change the initial value of i2 to $10.

**Action:** run 1 simulation.

**Grading:** The user turns 74 in 2029 and has $1010 in pre-tax retirement accounts. The distribution period for age 74 = 25.5. The RMD amount is $1010 / 25.5 = $39.61. Check that the stacked bar chart with breakdown of investments that in 2029:

1. The value of i2 decreases to 10 - 10 = 0.
2. The value of i1 decreases to 1000 - (39.61 - 10) = $970.39.
3. There is an investment with investment type i2, tax status non-retirement, and value $10.
   1. the stacked bar chart should show the amount $10 and a meaningful system-generated name for this automatically created investment. You don’t need to directly check that the investment type is i2 and the tax status is non-retirement.
4. There is an investment with investment type i1, tax status non-retirement, and value $29.61. \[an analogous grading comment applies as for the previous item.\]

# income test and federal income tax test

Share income.yaml with the team and ask them to import it, and skip the following edts, to save time. if the import fails, ask them to make the following edits to the previous scenario.

**Action:** add an event series to the above scenario.

Type: income

name: wages

Start year: uniform distribution, lower bound 2026, upper bound 2027.

Duration: 4

Initial amount: $40,000

Annual change: 0

Inflation-adjusted: yes

Social security? no

**Action:** change the value of the cash investment to 20000.

**Grading:** check:

1. when entering the start year, the UI gives a choice of (1) fixed value, (2) uniform distribution or normal distribution, (3) startsWith another event series, and (4) startsAfter another event series.
2. when entering the duration, the UI gives a choice of fixed value, uniform distribution and normal distribution.

**Action:** Run 20 simulations.

**Grading:** check:

1. The stacked bar chart of income with breakdown by event series shows that the average income from this event series in 2025 is 0, in 2026 is roughly $20k \[since it should be 0 in half of the sims, and $40k in the other half\], and in 2027 is $40k.
2. The stacked bar chart with expenses+tax breakdown shows that total tax in 2028 is $3176. Explanation of federal income tax (which is the only type of tax due): Federal taxable income in 2027 = income - std deduction = 40000 - 14600 = 28400. federal income tax brackets: 10% on income from $0 to $11600, and 12% on income from $11601 to 47150. Tax = 11600 \* 0.1 + (28400 - 11600) \* 0.12 = 3176.

# State income tax test

**Actions:**

Change user’s state of residence to NY

Change amount of ‘wages’ income event series to $20000

Run 1 sim.

**Grading:** check in the log or stacked bar chart of expenses+tax (whichever shows tax breakdown) that state income tax for 2027, paid in 2028, is $814.25. Explanation: NY tax rate schedule includes: “From 17,150 to 23,600, base $686 plus 4.5% of the excess over $17,150”. The user’s NY income tax is (20000-17150)\*0.045 + 686 = 814.25. If state income tax isn’t shown separately anywhere, record the total (federal+state) income tax paid in 2027, and we’ll analyze it later.

# State tax data upload test

**Action:** view the content of any state tax data yaml file that the team has created.

**Grading:** check that the file format contains lists of tax brackets for single people and married couples, and that the entry for each tax bracket includes these fields (possibly with different names): lower bound, upper bound, rate, base amount.

**Action:** import the file.

**Grading:** check that the import succeeds. Note: Displaying details of the uploaded data is not required.

# Roth Conversion Optimizer (RCO) test

**Action:** Edit the RCO settings in the above scenario as follows.

RCO: on (enabled)

RCO start year 2025, end year 2100

RCO strategy \[i1,i2\].

**Action:** edit the ‘wages’ event series as follows.

start year: 2025.

Initial amount: 61000

**Action:** run 1 simulation

**Grading:** check:

1. The log contains an entry for a Roth conversion of $750 in 2025. **Explanation:** Inflation is 0, so the federal tax brackets and standard deduction ($14,600 for singles) remain the same as the scraped ones (for 2024). The user’s federal taxable income in 2025 is 61000 - 14600 = 46400. the user’s marginal federal income tax bracket is “$11601 to 47150.“ The Roth conversion amount in 2025 is rc = 47150 - 46400 = 750.
2. the stacked bar chart of total investments with breakdown by investment shows in 2025 an investment with investment type it1 and amount $750 (it’s good but not required for the bar chart to indicate that the tax status is after-tax retirement). Note that the pre-tax investment of type it1 also still exists, with value 1000-750 = 250.

# one-dimensional scenario exploration test

**Action:** Run one-dimensional scenario exploration for the above scenario, with the Roth conversion optimization flag as a parameter, and 10 simulations per parameter value.

**Grading:** check that the number of simulations per parameter value can be specified.

**Action:** display multi-line chart of median total investments over time.

**Grading:** check that it contains two lines, one per parameter value.

# cyclic dependency test

**Action:** add an event series to the above scenario:

Type: expense

Description: car

Start year: startsWith wages

Duration: 1 year

Amount: $62,100

Annual change: 0

Inflation adjustment? no

Type: non-discretionary

**Action:** Enter the expense withdrawal strategy: i1, i2

**Actions:** change start year of ‘wages’ to startsWith ‘car’. Run 1 simulation if possible.

**Grading:** check the system prevents this or displays a detailed error message such as “cyclic dependency between start years of car and wages event series”. If not, record whether it reports a vague error message that the scenario is invalid, or whether it allows the simulation to proceed and if so, what happens, e.g., the system enters an infinite loop, or it uses particular start years for these event series.

# non-discretionary expense and early withdrawal tax test

Share nondiscretionaryExpense.yaml with the team and ask them to import it, and skip the following edts, to save time. if the import fails, ask them to make the following edits to the previous scenario.

**Action:** change the start year of ‘wages’ to 2025.

**Action:** change the user’s birth year to 2025, and life expectancy to 10.

**Action:** change the annual return of investment type it1 to fixed amount $600

**Action:** change the start year of ‘car’ to 2025.

**Action:** change the initial value of the cash investment to 0

**Action:** change the amount of ‘wages’ to $62000.

**Action:** Run 1 simulation.

**Grading:** check:

- Shaded line chart of early withdrawal tax shows that median early withdrawal tax in 2026 is $10.
- stacked bar chart of expenses+tax shows a $62,100 ‘car’ expense in 2025.
- stacked bar chart of investments with breakdown by investment shows that in 2025, the (end-of-year) investment values include: cash 0, i1 = 1000 + 600 - 100 = $1500.
- Log shows that no capital gains tax was paid in 2026.
- Log shows that $10 of early withdrawal tax was paid in 2026.

**Explanation:**

- In 2025, when the $62100 car expense is paid, the amount of cash available is initial value + wages = $62000. Therefore $62000 of the expense is paid from cash, and $100 is paid by selling $100 of investment i1. Note that the user does not pay any tax (for 2024) in 2025, because the project requirements (section 3) say “(2) For simplicity, the system assumes that no tax needs to be paid in the starting year of the simulation.”
- step 3 (update investments) of the simulation algorithm adds the annual return for 2025 to investment i1’s value before step 5 sells part of i1, so the investment’s value is 1000 + 600 = 1600 at the time of sale. The fraction of i1 sold is f = 100/1600 = .0625. The capital gain on the sold part is f \* (total capital gains) = .0625 \* 600 = $37.50.
- In 2026, the user pays early withdrawal tax on the 2025 early withdrawal from i1. The amount of tax is 10% \* $100 = $10.
- Note that there is no capital gains tax on sale of assets in retirement accounts.

# one-dimensional scenario exploration test

**Action:** Run one-dimensional scenario exploration for the above scenario, with the amount of the ‘car’ expense as a parameter ranging from 62,100 to 162,100 with step size 50,000, and 10 simulations per parameter value.

**Action:** display multi-line chart of probability of success over time.

**Grading:** check that it contains 3 lines, one per parameter value. The three lines overlap (i.e., have the same value) for some years, but at least one should differ from the other two in some years.

#

**Action:** display line chart of final value of probability of success as a function of parameter value.

**Action:** display line chart of final value of median total investments as a function of parameter value.

**Grading:** check that each chart contains a line connecting the values of the plotted quantities corresponding to the 3 values of the parameter, and the values look reasonable.

**Action:** View the stacked bar charts of investments for parameter value $162,100.

**Grading:** Check that this feature is supported. This feature is described in the project requirements (section 5) as “The user can also view (in the ways described in Section 4) the results for a selected parameter value.”

# two-dimensional scenario exploration test

#

**Action:** Run two-dimensional scenario exploration for the above scenario, adding duration of the ‘wages’ event series as a second parameter ranging from 2 to 6 with step 1, and other settings the same as before.

**Action:** display surface plot of final value of probability of success, as a function of the two parameters.

**Action:** display contour plot of final value of median total investments, as a function of the two parameters.

**Grading:** check that each chart shows the expected ranges for the two parameter values, and the values look reasonable.

**Action:** View the stacked bar charts of investments for the combination of parameter values car expense = $62,100, duration of wages = 2 years.

**Grading:** Check that this feature is supported. This feature is described in the project requirements (section 5) as “The user can also view (in the ways described in Section 4) the results for a selected combination of parameter values.”

# capital gains tax test

**Action:** change the tax status of investment i1 to non-retirement. View the Roth conversion strategy and the RMD strategy.

**Grading:** note that i1 is not pre-tax retirement and hence cannot be in either of those strategies. Check that the system either automatically removes i1 from those strategies, or displays a warning indicating that it must be removed. If the team says that this warning will be displayed when you try to run a simulation, that’s OK; try it.

**Action:** remove investment i1 from the Roth conversion strategy and the RMD strategy, if it wasn’t removed automatically.

**Action:** run 1 simulation.

**Grading:** check (in the log or stacked bar chart of expenses+tax, whichever shows tax breakdown) that $5.62 or $5.63 of capital gains tax was paid in 2026.

**Explanation:**

- In 2026, the user pays capital gains tax for 2025 on the $37.50 capital gain. The user’s overall taxable income in 2025 is wages + capital gains - std deduction = 62000 +37.5 - 14600 = 47437.5 “A [capital gains tax rate](https://www.irs.gov/taxtopics/tc409) of 15% applies if your taxable income is more than $47,025 but less than or equal to $518,900 for single”. Capital gains tax = 0.15 \* 37.5 = $5.62 or $5.63 depending on rounding direction.

# discretionary expense test

**Action:** make ‘car’ expense discretionary.

**Action:** Change financial goal to 63000

**Action:** Run 1 simulation.

**Grading:** check:

1. stacked bar chart of expenses+tax shows a $610 ‘car’ expense in 2025.
2. shaded line chart of percentage of discretionary expenses incurred shows that the median percentage incurred in 2025 is 1%.

**Explanation:** At the start of 2025, total assets = $1010. After adding wages and annual return of i1 in steps 1 and 3, total assets = 1010 + 62000 + 600 = 63610 when the car expense is processed in step 6. The car expense should be partially incurred (according to note 4 in section 2.3 of the project requirements). amount incurred = total assets - financial goal = 63610 - 63000 = $610. Percentage incurred = 610/62100 = 1%.

# invest test

Share invest.yaml with the team and ask them to import it, and skip the following edts, to save time; to quickly test the UI, ask them to make a change to the asset allocation and then undo the change. if the import fails, ask them to make the following edits to the previous scenario.

**Action:** change the user’s state of residence to AK (or other state for which state income tax will be 0).

**Action:** change the annual return of investment type it1 to 0.

**Action:** change the tax status of investment i2 to non-retirement

**Action:** Delete the ‘car’ expense event series.

**Action:** change the initial amount of ‘wages’ income event series to 1010.

**Action:** add an event series:

Name: v1

Type: invest

Start year: 2025

Duration: 3

Max cash: 10

Asset allocation: glide path with initial asset allocation i1 10%, i2 90%, and final asset allocation i1 30% , i2 70%.

**Action:** Run 1 simulation.

**Grading:** check that stacked bar chart of investments with breakdown by investment shows that in 2027, the (end-of-year) values are: i1 =1606, i2 = 2425, cash = 10.

**Grading of 2-person teams** (Caffeine Overload and CO2): they don’t need to implement glide paths. They can use the initial asset allocation as a fixed asset allocation. check that the stacked bar chart of investments with breakdown by investment shows that in 2025, the (end-of-year) values are: i1 =1100, i2 =910, cash = 10.

**Explanation:**

Initial values: i1 1000, i2 10, cash 0

Values after selected simulation steps in 2025:

step 1 (income events): cash 1010

Step 7 (invest events):

Amount to Invest: cash - max_cash = 1010 - 10 = 1000

I1 = 1000 + 0.10 \* 1000 = 1100, i2 = 10 + 0.9 \* 1000 = 910, cash = 10.

Values after selected simulation steps in 2026:

step 1 (income events): cash 10 + 1010 = 1020

Step 7 (invest events):

Amount to Invest: cash - max_cash = 1020 - 10 = 1010

I1 = 1100 + 0.20 \* 1010 = 1302, i2 = 910 + 0.8 \* 1010 = 1718, cash = 10

Values after selected simulation steps in 2027:

step 1 (income events): cash 10 + 1010 = 1020.

Step 7 (invest events):

Amount to Invest: cash - max_cash = 1020 - 10 = 1010.

I1 = 1302 + 0.30 \* 1010 = 1605, i2 = 1718 + 0.7 \* 1010 = 2425, cash = 10.

Note: the user pays no federal income tax, because taxable income is less than the standard deduction. The user pays no state income tax, because we selected a state for which state income tax data is not available. The user pays no capital gains tax, because all annual returns are 0.

# rebalance test

Share rebalance.yaml with the team and ask them to import it, and skip the following edts, to save time; to quickly test the UI, ask them to make a change to the asset allocation and then undo the change. if the import fails, ask them to make the following edits to the previous scenario.

**Action:** for investment type it2, change the annual return to fixed amount 1000.

**Action:** turn the Roth conversion optimizer off.

**Action:** remove i2 from the RMD strategy.

**Action:** for investment i2, change initial value to 100, and tax status to non-retirement

**Action:** for the ‘wages’ income event series, change start year to 2026, amount to 62000, and duration to 1 year.

**Action:** delete the ‘v1’ invest event series.

**Action:** add an event series:

Type: rebalance

Name: r1

Start year: 2026

Duration: 2

asset allocation: i1 60%, i2 40%.

**Action:** run 1 simulation.

**Grading:** check

- stacked bar chart of investments with breakdown by investment shows that in 2026, the (end-of-year) values are: i1 = 1860, i2 = 1240.
- Log shows that $122.86 of capital gains tax was paid in 2027.

**Action:** change the asset allocation to: i1 10%, i2 10%

**Grading:** Check that the system displays an error message stating that the asset allocation percentages don’t sum to 100%. It’s OK if the error message is displayed later, when the user attempts to run a simulation.

**Explanation for scenario with valid asset allocation:**

Initial values: i1 1000, i2 100, cash 0

In 2025: add annual return of i2. cash 0, i1 1000, i2 1100.

In 2026: add wages to cash and add annual return of i2. cash 62000, i1 1000, i2 2100.

Total assets to rebalance = 1000 + 2100 = 3100

target i1 = 0.6 \* 3100 = 1860, target i2 = 0.4 \* 3100 = 1240.

The fraction of i2 sold is f = (2100-1240)/2100 = 0.4095. The capital gain on the sold part is f \* (total capital gains) = ((2100-1240)/2100) \* 2000 = $819.05.

In 2027, the user pays some income tax (details unimportant) and capital gains tax. The user’s overall taxable income in 2026 is wages + capital gains - std deduction = 62000 + 819,05 - 14600 = 48219.05 “A [capital gains tax rate](https://www.irs.gov/taxtopics/tc409) of 15% applies if your taxable income is more than $47,025 but less than or equal to $518,900 for single”. Capital gains tax = 0.15 \* 819.05 = $122.86.

# event series deletion test

**Action:** Change start year of rebalance event series ‘r1’ to startsAfter ‘wages’.

**Action:** delete the ‘wages’ event series. Run 1 simulation if possible,

**Grading:** check that the system either

- prevents the deletion with an informative message such as “cannot delete an event series referenced by another event series”, or
- allows the deletion and subsequently (ideally, not necessarily, immediately) displays an informative error message such as “start year of r1 event series is invalid””.

# investment type deletion test

**Action:** delete investment type it1.

**Grading:** check that the system either

- prevents the deletion with an informative message such as “cannot delete an investment type referenced by an investment”, or
- automatically also deletes investment i1 (If the system does this without warning the user, record this, and we’ll probably give a UX penalty), or
- allows the deletion and subsequently (ideally immediately, but later is OK too) displays an informative error message such as “investment i1 has an invalid investment type”.
