import csv

def compare_csv_files(file1_path, file2_path):
    """
    Compare second columns of two CSV files and print unmatched entries
    
    Args:
        file1_path: Path to first CSV file
        file2_path: Path to second CSV file
    """
    # Read second column from both files
    file1_values = set()
    file2_values = set()
    
    # Read first file
    with open(file1_path, 'r') as f1:
        csv_reader = csv.reader(f1)
        next(csv_reader, None)  # Skip header if exists
        for row in csv_reader:
            if len(row) > 1:  # Ensure row has at least 2 columns
                file1_values.add(row[1])
    
    # Read second file
    with open(file2_path, 'r') as f2:
        csv_reader = csv.reader(f2)
        next(csv_reader, None)  # Skip header if exists
        for row in csv_reader:
            if len(row) > 1:
                file2_values.add(row[1])
    
    # Find differences
    in_file1_not_file2 = file1_values - file2_values
    in_file2_not_file1 = file2_values - file1_values
    
    # Print results
    if in_file1_not_file2:
        print(f"\nEntries in {file1_path} but not in {file2_path}:")
        for value in sorted(in_file1_not_file2):
            print(value)
    
    if in_file2_not_file1:
        print(f"\nEntries in {file2_path} but not in {file1_path}:")
        for value in sorted(in_file2_not_file1):
            print(value)
    
    if not in_file1_not_file2 and not in_file2_not_file1:
        print("\nAll entries match!")

# Example usage
if __name__ == "__main__":
    file1 = "file1.csv"
    file2 = "file2.csv"
    compare_csv_files(file1, file2)
