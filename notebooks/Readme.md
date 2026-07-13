# How to Read A/B Test Results as a Data PM
*5 Questions to Ask Before Declaring a Winner*

### 1. Was our sample size adequate from the start?
Never check a test early and stop it just because it looks like it's winning (peeking problem). Ensure both variants reached the required sample size calculated by the statistical power formula before drawing conclusions.

### 2. Is the result practically significant, or just statistically significant?
With a large enough sample size, even a $0.01\%$ difference can be statistically significant ($p < 0.05$). Ask: Does the size of this effect actually justify the engineering overhead and code complexity of deploying this feature? (The p-value answers the question: "If my new feature actually did absolutely nothing, what is the probability that I would see a success difference this large just by pure luck?")

### 3. Did we analyze user cohort breakdowns?
A winning treatment overall might hide toxic regressions in specific groups. Always slice the data by critical user segments (e.g., new vs. returning users, specific payment methods, mobile vs. desktop) to ensure it isn't hurting a core cohort.

### 4. What happened to our secondary guardrail metrics?
If your primary metric (Payment Success Rate) went up, did a secondary metric suffer? Check if the change caused an increase in customer support tickets, refund requests, or prolonged checkout latency. 

### 5. Have we accounted for the Novelty Effect?
Users often react positively or negatively to *change* itself, not the actual improvement. Run your tests for at least 1 to 2 full business cycles (minimum 1–2 weeks) to let the novelty wear off and capture true behavioral shifts.
