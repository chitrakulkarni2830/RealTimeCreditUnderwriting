import sqlite3
import pandas as pd
import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

def export_data_for_tableau():
    print("Initializing Data Export Pipeline for Tableau...")
    
    # Define paths
    db_path = os.path.join(root_dir, 'data', 'credit_data.db')
    output_csv_path = os.path.join(root_dir, 'data', 'tableau_export.csv')
    
    # The Master Query: Flattening Wide Utility data and Aggregating E-commerce data
    query = """
    WITH EcommerceAgg AS (
        SELECT 
            user_id,
            SUM(amount) as total_spend,
            SUM(CASE WHEN category = 'Essential' THEN amount ELSE 0 END) as essential_spend,
            SUM(CASE WHEN category = 'Luxury' THEN amount ELSE 0 END) as luxury_spend,
            COUNT(amount) as total_transactions,
            ROUND(AVG(amount), 2) as avg_transaction_size
        FROM ecommerce_spending
        GROUP BY user_id
    )
    SELECT 
        u.user_id,
        u.m1_elec_status, u.m1_elec_amt, u.m1_water_status, u.m1_water_amt,
        u.m2_elec_status, u.m2_elec_amt, u.m2_water_status, u.m2_water_amt,
        u.m3_elec_status, u.m3_elec_amt, u.m3_water_status, u.m3_water_amt,
        u.m4_elec_status, u.m4_elec_amt, u.m4_water_status, u.m4_water_amt,
        u.m5_elec_status, u.m5_elec_amt, u.m5_water_status, u.m5_water_amt,
        u.m6_elec_status, u.m6_elec_amt, u.m6_water_status, u.m6_water_amt,
        -- Calculate Total Utility Volume dynamically
        (u.m1_elec_amt + u.m1_water_amt + u.m2_elec_amt + u.m2_water_amt + 
         u.m3_elec_amt + u.m3_water_amt + u.m4_elec_amt + u.m4_water_amt + 
         u.m5_elec_amt + u.m5_water_amt + u.m6_elec_amt + u.m6_water_amt) as total_utility_volume,
        -- Detect any sequence of late payments
        CASE WHEN 'Late' IN (
            u.m1_elec_status, u.m1_water_status, u.m2_elec_status, u.m2_water_status,
            u.m3_elec_status, u.m3_water_status, u.m4_elec_status, u.m4_water_status,
            u.m5_elec_status, u.m5_water_status, u.m6_elec_status, u.m6_water_status
        ) THEN 1 ELSE 0 END as has_late_payment_flag,
        -- Join E-commerce Stats
        COALESCE(e.total_spend, 0) as total_ecommerce_spend,
        COALESCE(e.essential_spend, 0) as essential_spend,
        COALESCE(e.luxury_spend, 0) as luxury_spend,
        COALESCE(e.total_transactions, 0) as total_transactions,
        COALESCE(e.avg_transaction_size, 0) as avg_transaction_size,
        -- Calculate the core Behavioral Ratio
        ROUND(CAST(COALESCE(e.luxury_spend, 0) AS FLOAT) / 
              NULLIF(COALESCE(e.essential_spend, 0), 0), 2) as luxury_to_essential_ratio
    FROM utility_payments u
    LEFT JOIN EcommerceAgg e ON u.user_id = e.user_id
    ORDER BY u.user_id;
    """
    
    try:
        # Connect to DB and execute the master query
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Export to CSV
        df.to_csv(output_csv_path, index=False)
        print(f"✅ Success! Master Dataset exported to: {output_csv_path}")
        print(f"📊 Dataset Shape: {df.shape[0]} Rows, {df.shape[1]} Columns ready for Tableau.")
        
    except Exception as e:
        print(f"❌ Error during export: {e}")

if __name__ == "__main__":
    export_data_for_tableau()
