# 🧠 Feature Engineering & Risk Scoring Methodology

A cornerstone of the **Real-Time Credit Underwriting Agent** is its ability to transition from raw, unstructured data into a quantitative, deterministic **Risk Score (0-100)**. 

While the AI Agents provide qualitative reasoning, the deterministic scoring engine (`src/utils/scoring.py`) ensures compliance, fairness, and mathematical rigor.

## ⚖️ Feature Importance & Weighting

The algorithm begins with a perfect score of `100` and applies deductions based on two primary feature categories extracted from the user's data: **Fundamental Utility Reliability** (60% weight relative impact) and **Discretionary Behavioral Habits** (40% weight relative impact).

### 1. Fundamental Reliability: Late Payment History (High Impact)
The most predictive feature of future default is historical delinquency on essential bills.
*   **Feature**: Count of Late Utility Payments (Electricity & Water over 6 months).
*   **Penalty**: `-10 points per late instance`.
*   **Rationale**: A single late payment is a warning; multiple late payments indicate severe cash-flow distress. Because utility bills are typically prioritized by consumers, failing to meet these obligations heavily impacts the final score.

### 2. Behavioral Habit: Luxury-to-Essential Ratio (Medium Impact)
This engineered feature measures the applicant's financial maturity and prioritization.
*   **Feature**: Total Luxury Spend / Total Essential Spend.
*   **Penalty**: 
    *   Ratio > 2.0 (Discretionary Tilt): `-10 points`.
    *   Ratio > 5.0 (Extreme Luxury Focus): `-20 points`.
*   **Rationale**: Spending five times more on luxury goods than essential living costs suggests a high-risk lifestyle profile, making the applicant highly susceptible to economic shocks.

### 3. Behavioral Habit: Spending Volatility (Low-Medium Impact)
We calculate the standard deviation (or variance proxy) of daily/monthly e-commerce spending to measure lifestyle consistency.
*   **Feature**: Standard Deviation of E-commerce Transaction Amounts.
*   **Penalty**:
    *   Volatility > 100 (Moderate): `-5 points`.
    *   Volatility > 200 (High): `-15 points`.
*   **Rationale**: Highly volatile spending patterns make it difficult for an underwriter to predict future cash flow availability for debt servicing. Consistent, predictable spending is rewarded (no deduction).

## 🏆 Final Risk Tiers
After applying the feature penalties, the final score dictates the applicant's Underwriting Tier:
*   **Tier 1 (Premium)**: Score 80 - 100. (Eligible for highest credit limits and best APRs).
*   **Tier 2 (Standard)**: Score 50 - 79. (Eligible for standard limits with AI-suggested cautionary guardrails).
*   **Tier 3 (Subprime)**: Score < 50. (Subject to rejection or strict secured-limit provisioning).

---
*Note: This deterministic scoring layer acts in parallel to the CrewAI Agentic reasoning, providing a hybrid "AI + Math" underwriting decision.*
