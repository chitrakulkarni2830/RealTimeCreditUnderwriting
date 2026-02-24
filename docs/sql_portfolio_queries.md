# 📊 Real-Time Credit Underwriting: SQL Analysis Portfolio

This document contains 10 intermediate-to-advanced SQL queries designed to analyze the synthetic alternative credit data generated for this project. These queries demonstrate expertise in data manipulation, aggregation, window functions, and cross-table analysis using SQLite.

---

### Database Schema Overview
*   **`utility_payments` (Wide Format)**: Contains `user_id` and 24 columns representing 6 months of Electricity and Water bills (Status and Amount for each).
*   **`ecommerce_spending` (Long Format)**: Contains `user_id`, `date`, `category` ("Essential" or "Luxury"), `item`, and `amount`.

---

## 1. High-Level Category Split
*A fundamental aggregation to understand the overall distribution of e-commerce spending in the dataset.*

```sql
SELECT 
    category,
    COUNT(*) as total_transactions,
    SUM(amount) as total_revenue,
    ROUND(AVG(amount), 2) as average_transaction_value
FROM ecommerce_spending
GROUP BY category
ORDER BY total_revenue DESC;
```

## 2. Monthly Essential vs. Luxury Trends
*Extracts the month from the timestamp and pivots the categories to analyze temporal spending habits.*

```sql
SELECT 
    strftime('%Y-%m', date) as spending_month,
    SUM(CASE WHEN category = 'Essential' THEN amount ELSE 0 END) as essential_spend,
    SUM(CASE WHEN category = 'Luxury' THEN amount ELSE 0 END) as luxury_spend
FROM ecommerce_spending
GROUP BY spending_month
ORDER BY spending_month DESC;
```

## 3. The "Luxury Seekers" Ranking (Window Function)
*Uses a window function to rank users based on their total discretionary (Luxury) spending.*

```sql
WITH UserLuxuryTotals AS (
    SELECT 
        user_id,
        SUM(amount) as total_luxury_spend
    FROM ecommerce_spending
    WHERE category = 'Luxury'
    GROUP BY user_id
)
SELECT 
    user_id,
    total_luxury_spend,
    RANK() OVER (ORDER BY total_luxury_spend DESC) as luxury_rank
FROM UserLuxuryTotals
LIMIT 10;
```

## 4. Unpivoting Wide Utility Data (Advanced CTE)
*Transforms the wide `utility_payments` table into a structured long format to dynamically calculate total utility expenditure.*

```sql
WITH UnpivotedUtilities AS (
    SELECT user_id, 'Month 1' as month, 'Electricity' as type, m1_elec_status as status, m1_elec_amt as amount FROM utility_payments UNION ALL
    SELECT user_id, 'Month 1' as month, 'Water' as type, m1_water_status as status, m1_water_amt as amount FROM utility_payments UNION ALL
    SELECT user_id, 'Month 2' as month, 'Electricity' as type, m2_elec_status as status, m2_elec_amt as amount FROM utility_payments UNION ALL
    SELECT user_id, 'Month 2' as month, 'Water' as type, m2_water_status as status, m2_water_amt as amount FROM utility_payments
    -- (Expanded for brevity to all 6 months in actual execution)
)
SELECT 
    user_id,
    SUM(amount) as total_utility_spend_2_months,
    SUM(CASE WHEN status = 'Late' THEN 1 ELSE 0 END) as late_payment_count
FROM UnpivotedUtilities
GROUP BY user_id
ORDER BY late_payment_count DESC;
```

## 5. The Late Payment Risk Flag (Complex CASE)
*Scans across all 12 status columns in the wide table to instantly flag users with ANY history of delinquency.*

```sql
SELECT 
    user_id,
    CASE 
        WHEN 'Late' IN (
            m1_elec_status, m1_water_status, 
            m2_elec_status, m2_water_status, 
            m3_elec_status, m3_water_status, 
            m4_elec_status, m4_water_status, 
            m5_elec_status, m5_water_status, 
            m6_elec_status, m6_water_status
        ) THEN 'High Risk (Delinquent)'
        ELSE 'Reliable (Perfect History)'
    END as risk_profile
FROM utility_payments;
```

## 6. Luxury-to-Essential Ratio Analysis
*Calculates the critical consumer behavioral ratio used by the AI Agent for underwriting.*

```sql
SELECT 
    user_id,
    SUM(CASE WHEN category = 'Essential' THEN amount ELSE 0 END) as total_essentials,
    SUM(CASE WHEN category = 'Luxury' THEN amount ELSE 0 END) as total_luxury,
    ROUND(
        CAST(SUM(CASE WHEN category = 'Luxury' THEN amount ELSE 0 END) AS FLOAT) / 
        NULLIF(SUM(CASE WHEN category = 'Essential' THEN amount ELSE 0 END), 0), 2
    ) as luxury_to_essential_ratio
FROM ecommerce_spending
GROUP BY user_id
ORDER BY luxury_to_essential_ratio DESC;
```

## 7. Cross-Table Risk Correlation (JOIN)
*Investigates if users with late utility payments also exhibit higher discretionary spending.*

```sql
WITH UtilityDelinquency AS (
    SELECT 
        user_id,
        CASE WHEN 'Late' IN (m1_elec_status, m1_water_status, m2_elec_status) THEN 1 ELSE 0 END as is_delinquent
    FROM utility_payments
),
UserSpending AS (
    SELECT 
        user_id, 
        ROUND(AVG(amount), 2) as avg_transaction_size
    FROM ecommerce_spending 
    WHERE category = 'Luxury'
    GROUP BY user_id
)
SELECT 
    u.is_delinquent,
    COUNT(u.user_id) as number_of_users,
    ROUND(AVG(s.avg_transaction_size), 2) as average_luxury_transaction_size
FROM UtilityDelinquency u
LEFT JOIN UserSpending s ON u.user_id = s.user_id
GROUP BY u.is_delinquent;
```

## 8. Identifying Spending Volatility (Standard Deviation Proxy)
*Since SQLite lacks a native STDEV function, we calculate the Variance manually to assess spending stability.*

```sql
WITH UserStats AS (
    SELECT user_id, AVG(amount) as avg_spend, COUNT(*) as txn_count
    FROM ecommerce_spending
    GROUP BY user_id
)
SELECT 
    e.user_id,
    COUNT(e.amount) as total_txns,
    ROUND(AVG(e.amount), 2) as average_spend,
    -- Variance approximation
    ROUND(SUM((e.amount - u.avg_spend) * (e.amount - u.avg_spend)) / (u.txn_count - 1), 2) as spending_variance
FROM ecommerce_spending e
JOIN UserStats u ON e.user_id = u.user_id
GROUP BY e.user_id
HAVING total_txns > 2
ORDER BY spending_variance DESC;
```

## 9. Most Frequently Financed Items
*Identifies specific items that appear most often in the transaction history.*

```sql
SELECT 
    item,
    category,
    COUNT(*) as purchase_frequency,
    MAX(amount) as max_price_paid
FROM ecommerce_spending
GROUP BY item, category
ORDER BY purchase_frequency DESC
LIMIT 5;
```

## 10. The Comprehensive Underwriter's View (Master Dashboard Query)
*A consolidated materialization query combining behavior, history, and financial volume into a single snapshot.*

```sql
WITH EcommerceSummary AS (
    SELECT 
        user_id,
        SUM(amount) as total_ecommerce_spend,
        SUM(CASE WHEN category = 'Luxury' THEN amount ELSE 0 END) as luxury_spend
    FROM ecommerce_spending
    GROUP BY user_id
)
SELECT 
    u.user_id,
    (u.m1_elec_amt + u.m1_water_amt + u.m2_elec_amt + u.m6_water_amt) as est_utility_volume,
    CASE WHEN 'Late' IN (u.m1_elec_status, u.m1_water_status) THEN 'Yes' ELSE 'No' END as recent_late_payment,
    COALESCE(e.total_ecommerce_spend, 0) as total_ecommerce_spend,
    ROUND(COALESCE(e.luxury_spend, 0) * 100.0 / NULLIF(e.total_ecommerce_spend, 0), 1) as percent_luxury
FROM utility_payments u
LEFT JOIN EcommerceSummary e ON u.user_id = e.user_id
ORDER BY u.user_id ASC;
```
