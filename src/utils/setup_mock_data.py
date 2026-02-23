import pandas as pd
import json
import random
import sqlite3
import os
from datetime import datetime, timedelta

# =================================================================
# SYNTHETIC DATA GENERATOR (COMPREHENSIVE WIDE FORMAT + SQLITE)
# Generates realistic alternative financial data for 50 users.
# Outputs: 
# 1. data/utility_payments.csv (Wide Format)
# 2. data/ecommerce_spending.json (Transaction List)
# 3. data/credit_data.db (SQLite Database with 2 tables)
# =================================================================

def generate_data(num_users=50):
    utility_rows = []
    ecommerce_records = []
    
    # Categories for e-commerce
    essentials = ["Groceries", "Utilities", "Rent", "Insurance", "Pharmacy"]
    luxuries = ["Designer Clothes", "Gourmet Dining", "Electronics", "Travel", "Subscription"]

    for user_id in range(1, num_users + 1):
        # Determine User Risk Profile
        if user_id <= 10:
            profile = "Reliable"
        elif user_id <= 20:
            profile = "High Risk"
        else:
            profile = "Average"

        # 1. Generate Utility Payments (Status + Amounts)
        user_utility_row = {"user_id": user_id}
        
        for i in range(1, 7): # Last 6 months
            for bill in ["elec", "water"]:
                amount = random.randint(30, 150)
                
                # Status Logic based on profile
                if profile == "Reliable":
                    status = "Paid"
                elif profile == "High Risk":
                    status = random.choice(["Paid", "Paid", "Late"]) 
                else:
                    status = random.choice(["Paid"] * 9 + ["Late"])
                
                # Column names
                status_col = f"m{i}_{bill}_status"
                amt_col = f"m{i}_{bill}_amt"
                
                user_utility_row[status_col] = status
                user_utility_row[amt_col] = amount
        
        utility_rows.append(user_utility_row)

        # 2. Generate E-commerce Spending
        num_transactions = 10 if profile == "High Risk" else 5
        for _ in range(num_transactions):
            date = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
            
            if profile == "Reliable":
                category = "Essential"
                item = random.choice(essentials)
                amount = random.randint(20, 100)
            elif profile == "High Risk":
                category = random.choice(["Essential", "Luxury", "Luxury"]) 
                item = random.choice(luxuries if category == "Luxury" else essentials)
                amount = random.randint(100, 1000) if category == "Luxury" else random.randint(20, 100)
            else:
                category = random.choice(["Essential", "Essential", "Luxury"])
                item = random.choice(luxuries if category == "Luxury" else essentials)
                amount = random.randint(50, 300) if category == "Luxury" else random.randint(20, 100)

            ecommerce_records.append({
                "user_id": user_id,
                "date": date,
                "category": category,
                "item": item,
                "amount": amount
            })

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # A. Save Utility Data (CSV)
    df_utils = pd.DataFrame(utility_rows)
    df_utils.to_csv('data/utility_payments.csv', index=False)
    
    # B. Save E-commerce Data (JSON)
    with open('data/ecommerce_spending.json', 'w') as f:
        json.dump(ecommerce_records, f, indent=2)

    # C. Save to SQLite Database
    db_path = 'data/credit_data.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    # Write utility payments table
    df_utils.to_sql('utility_payments', conn, index=False)
    
    # Write ecommerce spending table
    df_ecom = pd.DataFrame(ecommerce_records)
    df_ecom.to_sql('ecommerce_spending', conn, index=False)
    
    conn.close()

    print(f"Successfully generated comprehensive data for {num_users} users.")
    print(f"- Saved to data/utility_payments.csv")
    print(f"- Saved to data/ecommerce_spending.json")
    print(f"- Created SQLite Database: {db_path} (Tables: utility_payments, ecommerce_spending)")

if __name__ == "__main__":
    generate_data(50)
