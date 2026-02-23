import json
import re
import pandas as pd
from src.utils import get_resource_path

# =================================================================
# GOLD STANDARD SIMULATION ENGINE (WIDE FORMAT V2)
# This class provides the exact same analytical logic as our 
# agents and tools but without any external dependencies on 
# LangChain or CrewAI. This ensures it runs for FREE.
# Supports 'Status + Amount' wide schema.
# =================================================================

class LocalCreditSimulator:
    """
    Simulates the Data Aggregator, Behavioral Analyst, and Underwriter.
    Supports Comprehensive Wide Format (Status + Amount).
    """
    
    def __init__(self, user_id):
        self.user_id = int(user_id)

    def fetch_utility_data(self):
        """Standalone version of the status + amount utility tool logic."""
        try:
            csv_path = get_resource_path('data/utility_payments.csv')
            df = pd.read_csv(csv_path)
            user_row = df[df['user_id'] == self.user_id]
            
            if user_row.empty:
                return "Late: 0, Total Billed: $0.00 (No data found)"
            
            # Extract all status and amount columns
            status_cols = [col for col in df.columns if "_status" in col]
            amt_cols = [col for col in df.columns if "_amt" in col]
            
            user_statuses = user_row[status_cols].values.flatten()
            user_amounts = user_row[amt_cols].values.flatten()
            
            late_count = sum(1 for s in user_statuses if s == "Late")
            total_billed = sum(user_amounts)
            
            return f"Late: {late_count}, Total Billed: ${total_billed:,.2f}"
        except:
            return "Late: 0, Total Billed: $0.00"

    def analyze_spending_data(self):
        """Standalone version of the e-commerce tool logic."""
        try:
            json_path = get_resource_path('data/ecommerce_spending.json')
            with open(json_path, 'r') as f:
                data = json.load(f)
            df = pd.DataFrame([t for t in data if t['user_id'] == self.user_id])
            
            if df.empty: 
                return {"spending_volatility": 0, "luxury_vs_essential_ratio": 0}
            
            volatility = df.groupby('date')['amount'].sum().std()
            essential = df[df['category'] == 'Essential']['amount'].sum()
            luxury = df[df['category'] == 'Luxury']['amount'].sum()
            ratio = (luxury / essential) if essential > 0 else luxury
            
            return {
                "spending_volatility": round(volatility if not pd.isna(volatility) else 0, 2),
                "luxury_vs_essential_ratio": round(ratio, 2)
            }
        except:
            return {"spending_volatility": 0, "luxury_vs_essential_ratio": 0}

    def run(self):
        print(f"\n[SIMULATION] Phase 1: Data Aggregator is fetching records...")
        utility_summary = self.fetch_utility_data()
        ecom_stats = self.analyze_spending_data()
        
        print(f"[SIMULATION] Phase 2: Behavioral Analyst is identifying patterns...")
        volatility = ecom_stats["spending_volatility"]
        ratio = ecom_stats["luxury_vs_essential_ratio"]
        
        # Parse utility summary for cleaner display
        # "Late: N, Total Billed: $X.XX"
        late_count = int(utility_summary.split(',')[0].split(':')[1].strip())
        total_billed = utility_summary.split('$')[1].strip()

        print(f"[SIMULATION] Phase 3: Senior Underwriter is drafting the detailed profile review...")
        
        status = "PREMIUM APPROVAL" if late_count == 0 and ratio < 1.0 else "CAUTIONARY REVIEW" if late_count <= 1 else "REJECTED"
        
        result = [
            f"### 📑 DETAILED CREDIT ASSESSMENT: {status}",
            "\n#### 🛡️ Financial Stability Assessment",
            f"An exhaustive analysis of the applicant's alternative utility payment history reveals a **{'highly reliable' if late_count == 0 else 'moderately consistent'}** payment pattern. "
            f"The applicant has processed a total billing volume of **${total_billed}** over the observed 6-month period. "
            f"{'Zero late payments were detected, signifying an elite level of cash-flow discipline.' if late_count == 0 else f'A total of {late_count} late payment(s) were flagged, suggesting periodic liquidity challenges.'}",
            
            "\n#### 🧠 Consumer Behavioral Profile",
            f"Mathematical modeling of e-commerce transactions indicates a **{'conservative' if ratio < 0.5 else 'balanced' if ratio < 1.5 else 'aggressive'}** lifestyle profile. "
            f"Spending volatility is measured at **{volatility:.2f}**, which represents a **{'remarkably steady' if volatility < 50 else 'stable' if volatility < 150 else 'fluctuating'}** consumption habit. "
            f"The Luxury-to-Essential ratio stands at **{ratio:.2f}**, demonstrating that for every dollar spent on essentials, the applicant prioritizes **${ratio:.2f}** on discretionary luxury items.",
            
            "\n#### ⚖️ Underwriting Recommendations",
            f"Based on the synthesized behavioral and financial data layers, we propose a starting credit limit of **${'5,000' if status == 'PREMIUM APPROVAL' else '1,500' if status == 'CAUTIONARY REVIEW' else '500'}**. "
            "Our decision is supported by the applicant's historical repayment consistency and their demonstrated ability to navigate discretionary spending without compromising core financial obligations."
        ]
        
        return "\n".join(result)
