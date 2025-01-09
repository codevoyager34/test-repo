def compare_first_columns(file1_path, file2_path):
   # Lists to store first column values
   file1_values = []
   file2_values = []

   # Read first file
   with open(file1_path, 'r') as f1:
       for line in f1:
           columns = line.strip().split(',')
           file1_values.append(columns[0])

   # Read second file  
   with open(file2_path, 'r') as f2:
       for line in f2:
           columns = line.strip().split(',')
           file2_values.append(columns[0])

   # Compare and print differences
   print("\nValues in file1 but not in file2:")
   for value in file1_values:
       if value not in file2_values:
           print(value)

   print("\nValues in file2 but not in file1:")
   for value in file2_values:
       if value not in file1_values:
           print(value)

# Example usage
file1 = "file1.txt"
file2 = "file2.txt"
compare_first_columns(file1, file2)
