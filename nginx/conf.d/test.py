
import sys
from pathlib import Path

def compare_files(file1_path: str, file2_path: str):
   try:
       with open(file1_path) as f1, open(file2_path) as f2:
           lines1 = set(line.strip() for line in f1)
           lines2 = set(line.strip() for line in f2)
           
           missing_in_file2 = lines1 - lines2
           missing_in_file1 = lines2 - lines1
           
           print(f"\nMissing in {file2_path}:")
           for line in sorted(missing_in_file2):
               print(line)
               
           print(f"\nMissing in {file1_path}:")
           for line in sorted(missing_in_file1):
               print(line)

   except FileNotFoundError as e:
       print(f"Error: {e.filename} not found")
   except Exception as e:
       print(f"Error: {e}")

if __name__ == "__main__":
   if len(sys.argv) != 3:
       print("Usage: python script.py file1.txt file2.txt")
       sys.exit(1)
       
   compare_files(sys.argv[1], sys.argv[2])





#################################




-- First check affected rows:
SELECT COUNT(*) as rows_to_move 
FROM new_application_property 
WHERE property_name ILIKE '%password%';

-- See which properties will be moved:
SELECT DISTINCT property_name 
FROM new_application_property 
WHERE property_name ILIKE '%password%';

BEGIN;

CREATE TABLE temp_password AS 
SELECT * FROM new_application_property WHERE FALSE;

INSERT INTO temp_password
SELECT * FROM new_application_property 
WHERE property_name ILIKE '%password%';

DELETE FROM new_application_property 
WHERE property_name ILIKE '%password%';

COMMIT;

-- Rollback if needed:
/*
BEGIN;
   INSERT INTO new_application_property 
   SELECT * FROM temp_password;
   DROP TABLE temp_password;
COMMIT;
*/
