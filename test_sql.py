import sqlite3
import re

with open('sql_portfolio_queries.md', 'r') as f:
    text = f.read()

queries = re.findall(r'```sql\n(.*?)```', text, re.DOTALL)

conn = sqlite3.connect('data/credit_data.db')
cursor = conn.cursor()

for i, q in enumerate(queries, 1):
    try:
        cursor.execute(q)
        cursor.fetchall()
        print(f"Query {i} OK")
    except Exception as e:
        print(f"Query {i} ERROR: {e}")

conn.close()
