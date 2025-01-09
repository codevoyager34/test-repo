def compare_files(file1_path, file2_path):
    # Read file1
    file1_values = []
    with open(file1_path, 'r') as f1:
        for line in f1:
            if ',' in line:  # Make sure line has a comma
                file1_values.append(line.strip().split(',')[1])  # Get second column

    # Read file2
    file2_values = []
    with open(file2_path, 'r') as f2:
        for line in f2:
            if ',' in line:
                file2_values.append(line.strip().split(',')[1])

    # Compare and print differences
    print(f"\nChecking values from {file1_path} against {file2_path}:")
    for value in file1_values:
        if value not in file2_values:
            print(f"Not found in {file2_path}: {value}")

    print(f"\nChecking values from {file2_path} against {file1_path}:")
    for value in file2_values:
        if value not in file1_values:
            print(f"Not found in {file1_path}: {value}")

# Example usage
file1 = "file1.txt"
file2 = "file2.txt"
compare_files(file1, file2)
