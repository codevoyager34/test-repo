import psycopg2
import csv
from datetime import datetime

# DB connection
db = psycopg2.connect(
    host='localhost',
    database='your_db',
    user='your_user',
    password='your_pass'
)
cursor = db.cursor()

# Get all tables
cursor.execute("""
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'cmdbv3'
""")
tables = [table[0] for table in cursor.fetchall()]

# Scan each table for tokens
results = []
for table in tables:
    print(f"Scanning table: {table}")
    query = f"""
    SELECT 
        jsonb_object_keys(properties) as prop_name,
        properties ->> jsonb_object_keys(properties) as prop_value,
        '{table}' as table_name
    FROM cmdbv3.{table}
    WHERE 
        properties::text ILIKE '%password%' OR 
        properties::text ILIKE '%pwd%' OR
        properties::text ILIKE '%token%'
    """
    cursor.execute(query)
    results.extend(cursor.fetchall())

# Save results to CSV
filename = f'token_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Property Name', 'Property Value', 'Table Name'])
    writer.writerows(results)

print(f"Scan complete. Results saved to {filename}")
cursor.close()
db.close()
