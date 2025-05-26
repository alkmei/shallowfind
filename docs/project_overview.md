### Project Overview: Lifetime Financial Planner (LFP)

### CSE 416: Software Engineering, Spring 2025

### Professor Scott D. Stoller

### version: 2025-01-27

Goal. Financial planning is challenging because of the wide variety of available investments, the complexity of tax rules, and the unpredictability of the future. Financial planning software allows users to analyze the outcomes of their plans for investments, retirement age, and other financial decisions under various assumptions about the future. The goal of this project is to develop a lifetime financial planner (LFP) that analyzes life-long financial plans spanning a user’s career and retirement. Financial plans include decisions about asset allocation (allocation of assets among different types of investments: domestic stocks, foreign stocks, bonds, etc.), retirement age, whether to save for retirement in traditional (pre-tax) retirement accounts or Roth retirement accounts, etc. Financial planning is tightly coupled with life planning: buying a house, having children, etc.

Approach. LFP should use Monte Carlo simulations to evaluate financial plans. In Monte Carlo simulations, future behavior of financial markets---investment gains, inflation rate, etc.---and potentially other variables are modeled probabilistically, using probability distributions such as normal distributions or Markov processes such as [geometric Brownian motion](https://www.investopedia.com/articles/07/montecarlo.asp) (GBM). Many simulations are performed, and the results are summarized to give users insight into their financial futures, including the likelihood of their meeting their long-term financial goals.

Scope. Financial planning is a vast topic. LFP should focus on the financial decisions mentioned in the opening paragraph. It should allow users to model the financial effects of major life events such as marriage, having children, and death of a spouse. It should consider income tax, capital gains tax, and early withdrawal tax (on early withdrawals from retirement accounts); other taxes can be ignored. Details of government programs such as Social Security and Medicare are out of scope; for example, users can specify social security as an income source but are responsible for estimating the amount themselves.

Decision support. LFP should conveniently support comparing results based on different sets of assumptions, such as different asset allocations, different retirement ages, and use of different types of retirement accounts.

Flexibility. LFP should be flexible. For example, it should allow users to define investment types; it may provide some pre-defined investment types but should not be limited to those.

UX. LFP should provide an easy-to-use GUI that includes explanatory text and links to relevant information on the web. It should offer a rich set of customizable charts to help users understand the analysis results.

Deployment. LFP should be a web application that supports saving financial plans and sharing them with other users, such as family members and financial planners.

Try it! You should examine and experiment with some existing financial planning / retirement planning tools. Many financial companies, such as Fidelity and Charles Schwab, provide such tools on their websites. However, these require creating accounts. It is fine to examine only tools that don’t require revealing your identity. This includes some websites as well as open-source tools (on github, etc.). In the former category, I recommend [Incomewize](https://incomewize.com) and [ProjectionLab](https://projectionlab.com/) (if you don’t want to register with an email address, select “Try it now!” then “Skip sign up for now”) .

Motivation. I hope this project will provide useful financial knowledge as well as software engineering experience.
