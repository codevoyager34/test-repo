def print_before_comma(file_path):
    print(f"\nPrinting content from: {file_path}")
    with open(file_path, 'r') as f:
        for line in f:
            # Debug print to see what we're reading
            print("Original line:", line.strip())
            
            if ',' in line:
                columns = line.split(',')
                print("Split result:", columns)
                print("First part:", columns[0])
                print("---")

# Example usage
file_path = "your_file.txt"
print_before_comma(file_path)
