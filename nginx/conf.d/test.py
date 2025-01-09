import csv

def compare_csv_files(file1_path, file2_path):
    """
    Compare second column values between two CSV files row by row
    """
    # Read all second column values from file2 first for comparison
    file2_values = []
    with open(file2_path, 'r') as f2:
        reader = csv.reader(f2)
        next(reader, None)  # Skip header
        for row in reader:
            if len(row) > 1:
                file2_values.append(row[1])

    print(f"\nChecking values from {file1_path} against {file2_path}:")
    # Compare file1 values against file2
    with open(file1_path, 'r') as f1:
        reader = csv.reader(f1)
        next(reader, None)  # Skip header
        for row in reader:
            if len(row) > 1:
                value = row[1]
                if value not in file2_values:
                    print(f"Not found in {file2_path}: {value}")

    print(f"\nChecking values from {file2_path} against {file1_path}:")
    # Read all second column values from file1 for reverse comparison
    file1_values = []
    with open(file1_path, 'r') as f1:
        reader = csv.reader(f1)
        next(reader, None)  # Skip header
        for row in reader:
            if len(row) > 1:
                file1_values.append(row[1])

    # Compare file2 values against file1
    with open(file2_path, 'r') as f2:
        reader = csv.reader(f2)
        next(reader, None)  # Skip header
        for row in reader:
            if len(row) > 1:
                value = row[1]
                if value not in file1_values:
                    print(f"Not found in {file1_path}: {value}")

# Example usage
if __name__ == "__main__":
    file1 = "file1.csv"
    file2 = "file2.csv"
    compare_csv_files(file1, file2)
