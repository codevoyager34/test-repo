def print_second_column(file_path):
    print(f"\nPrinting second column from: {file_path}")
    with open(file_path, 'r') as f:
        for line in f:
            if ',' in line:
                columns = line.strip().split(',')
                if len(columns) > 1:  # Make sure we have at least 2 columns
                    print(columns[1])  # Print second column

# Example usage
file1 = "file1.txt"
print_second_column(file1)
