import pandas as pd
import json
import os
import sqlite3
from src.utils import get_resource_path
from langchain.tools import tool

# =================================================================
# CUSTOM TOOLS FOR ALTERNATIVE DATA ANALYSIS (WIDE FORMAT + SQLITE)
# These tools support CSV, JSON, and SQLite (Premium Tier).
# =================================================================

class FinancialDataTools:
    
    @tool("fetch_utility_history")
    def fetch_utility_history(user_id: int, source: str = "csv"):
        """
        Fetches the utility payment history for a specific User ID.
        Supports 'csv' or 'sqlite' sources. Default is 'csv'.
        Analyzes the wide-format table (Status + Amounts).
        """
        try:
            if source == "sqlite":
                db_path = get_resource_path('data/credit_data.db')
                conn = sqlite3.connect(db_path)
                query = f"SELECT * FROM utility_payments WHERE user_id = {int(user_id)}"
                user_row = pd.read_sql_query(query, conn)
                conn.close()
            else:
                csv_path = get_resource_path('data/utility_payments.csv')
                df = pd.read_csv(csv_path)
                user_row = df[df['user_id'] == int(user_id)]
            
            if user_row.empty:
                return f"No utility data found for User ID {user_id}."
            
            # Extract all status and amount columns
            status_cols = [col for col in user_row.columns if "_status" in col]
            amt_cols = [col for col in user_row.columns if "_amt" in col]
            
            user_statuses = user_row[status_cols].values.flatten()
            user_amounts = user_row[amt_cols].values.flatten()
            
            late_count = sum(1 for s in user_statuses if s == "Late")
            total_billed = sum(user_amounts)
            total_records = len(user_statuses)
            
            summary = (
                f"Utility Payment Summary for User {user_id} (Source: {source.upper()}):\n"
                f"- Data Structure: High-fidelity Wide Format (Status + Amounts)\n"
                f"- Total Payment Windows: {total_records}\n"
                f"- Late Payments Detected: {late_count}\n"
                f"- Total Billed Amount (6mo): ${total_billed:,.2f}\n"
                f"- Payment Consistency: {((total_records - late_count)/total_records)*100:.1f}%"
            )
            return summary
            
        except Exception as e:
            return f"Critical Error in utility tool: {str(e)}"

    @tool("analyze_ecommerce_spending")
    def analyze_ecommerce_spending(user_id: int):
        """
        Analyzes e-commerce transactions to identify spending behavior.
        Calculates Volatility (Standard Deviation) and Luxury/Essential Ratios.
        """
        try:
            json_path = get_resource_path('data/ecommerce_spending.json')
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            user_transactions = [t for t in data if t['user_id'] == int(user_id)]
            
            if not user_transactions:
                return f"No e-commerce data found for User ID {user_id}."
            
            df = pd.DataFrame(user_transactions)
            
            # 1. Calculate Spending Volatility
            daily_spending = df.groupby('date')['amount'].sum()
            volatility = daily_spending.std() if len(daily_spending) > 1 else 0
            
            # 2. Calculate Luxury vs Essential Ratio
            essential_total = df[df['category'] == 'Essential']['amount'].sum()
            luxury_total = df[df['category'] == 'Luxury']['amount'].sum()
            
            ratio = (luxury_total / essential_total) if essential_total > 0 else luxury_total
            
            profile = {
                "user_id": user_id,
                "spending_volatility": round(volatility, 2) if not pd.isna(volatility) else 0,
                "luxury_vs_essential_ratio": round(ratio, 2),
                "total_spending": df['amount'].sum(),
                "top_expense_category": df.groupby('category')['amount'].sum().idxmax()
            }
            
            return json.dumps(profile, indent=2)
            
        except Exception as e:
            return f"Error in e-commerce tool: {str(e)}"
