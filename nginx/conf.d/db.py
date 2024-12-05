import psycopg2
import csv
from datetime import datetime

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

results = []
for table in tables:
    print(f"Scanning table: {table}")
    
    # Get all columns for this table
    cursor.execute(f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'cmdbv3' 
        AND table_name = '{table}'
    """)
    columns = [col[0] for col in cursor.fetchall()]
    
    # Scan each column
    for column in columns:
        try:
            # Check if column is JSON/JSONB type
            if column == 'properties':
                query = f"""
                SELECT 
                    jsonb_object_keys(properties) as prop_name,
                    properties ->> jsonb_object_keys(properties) as prop_value,
                    '{table}' as table_name,
                    'properties' as source_column
                FROM cmdbv3.{table}
                WHERE 
                    properties::text ILIKE '%password%' OR 
                    properties::text ILIKE '%pwd%' OR
                    properties::text ILIKE '%token%'
                """
            else:
                # For regular columns
                query = f"""
                SELECT 
                    '{column}' as prop_name,
                    {column}::text as prop_value,
                    '{table}' as table_name,
                    '{column}' as source_column
                FROM cmdbv3.{table}
                WHERE 
                    {column}::text ILIKE '%password%' OR 
                    {column}::text ILIKE '%pwd%' OR
                    {column}::text ILIKE '%token%'
                """
            
            cursor.execute(query)
            results.extend(cursor.fetchall())
            
        except (psycopg2.Error, psycopg2.Warning) as e:
            print(f"Error scanning {table}.{column}: {str(e)}")
            continue

filename = f'token_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Property Name', 'Property Value', 'Table Name', 'Source Column'])
    writer.writerows(results)

print(f"Scan complete. Results saved to {filename}")
cursor.close()
db.close()
