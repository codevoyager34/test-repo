def print_before_comma(file_path):
    print(f"\nPrinting first column from: {file_path}")
    with open(file_path, 'r') as f:
        for line in f:
            if ',' in line:
                first_column = line.split(',')[0]
                print(first_column)

# Example usage
file1 = "file1.txt"
print_before_comma(file1)
