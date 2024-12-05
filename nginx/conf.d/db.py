import psycopg2
import csv


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

patterns = [
    '%password%', '%PASSWORD%', '%Password%',
    '%pwd%', '%PWD%', '%Pwd%',
    '%token%', '%TOKEN%', '%Token%'
]

query = """
SELECT 
    jsonb_object_keys(properties) as prop_name,
    properties ->> jsonb_object_keys(properties) as prop_value,
    'new_application_level_property' as table_name
FROM cmdbv3.new_application_level_property
WHERE 
    properties::text ILIKE ANY(ARRAY{})
""".format(patterns)

cursor.execute(query)
results = cursor.fetchall()

filename = f'token_scan_single_table_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
with open(filename, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Property Name', 'Property Value', 'Table Name'])
    writer.writerows(results)

print(f"Found {len(results)} matches. Results saved to {filename}")
cursor.close()
db.close()
