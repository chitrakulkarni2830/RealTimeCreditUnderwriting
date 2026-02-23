import pandas as pd
import json

# 1. Behavioral Analyst Logic
# I am a fresher learning python, so I will code simply!

def analyze_behavior(user_id):
    # Load utility data
    # I use pandas because it's good for tables
    utils_df = pd.read_csv('data/utility_payments.csv')
    user_utils = utils_df[utils_df['user_id'] == user_id]
    
    # Load ecommerce data (this looks like an API but it's a file)
    with open('data/ecommerce_spending.json', 'r') as f:
        ecom_data = json.load(f)
    
    user_ecom = [item for item in ecom_data if item['user_id'] == user_id]
    ecom_df = pd.DataFrame(user_ecom)

    # Calculation 1: Spending Volatility (Standard Deviation)
    # How much does their spending jump around?
    if not ecom_df.empty:
        # Group by date to get daily spend, then take standard deviation
        volatility = ecom_df.groupby('date')['amount'].sum().std()
    else:
        volatility = 0

    # Calculation 2: Essential vs Luxury Ratio
    if not ecom_df.empty:
        essential = ecom_df[ecom_df['category'] == 'Essential']['amount'].sum()
        luxury = ecom_df[ecom_df['category'] == 'Luxury']['amount'].sum()
        
        if essential > 0:
            ratio = luxury / essential
        else:
            ratio = luxury # if no essential, ratio is just luxury amount
    else:
        ratio = 0
        essential = 0
        luxury = 0

    # Calculation 3: Late Payments
    late_payments = len(user_utils[user_utils['status'] == 'Late'])

    return {
        "user_id": user_id,
        "volatility": volatility,
        "luxury_ratio": ratio,
        "late_payments": late_payments,
        "total_essential": essential,
        "total_luxury": luxury
    }

# 2. Underwriter prompt template
# This is a template for the AI to follow

underwriter_prompt_template = """
Role: Senior Fintech Underwriter
Context: You are reviewing an agentic financial health profile for User ID: {user_id}.

Input Data:
- Spending Volatility: {volatility}
- Luxury vs Essential Ratio: {luxury_ratio} (Lower is usually better)
- Late Utility Payments: {late_payments}
- Total Essential Spend: {total_essential}
- Total Luxury Spend: {total_luxury}

Task: Write a 3-paragraph "Decision Summary" justifying a credit limit.
Paragraph 1: Discuss their stability based on utility payments and spending volatility.
Paragraph 2: Analyze their spending habits (Luxury vs Essential ratio).
Paragraph 3: Final Decision. State the suggested credit limit (e.g., $500, $2000, or $5000) and why.

Tone: Professional, analytical, and fair.
"""

# Test the logic for a user
if __name__ == "__main__":
    result = analyze_behavior(101)
    print("--- Behavioral Analysis Results ---")
    print(result)
    
    print("\n--- Underwriter Prompt Mockup ---")
    prompt = underwriter_prompt_template.format(**result)
    print(prompt)
