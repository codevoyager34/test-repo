import pandas as pd

# Step 1: Load the two CSVs
csv1 = pd.read_csv("machine1.csv")  # Replace with your first CSV file
csv2 = pd.read_csv("machine2.csv")  # Replace with your second CSV file

# Step 2: Merge both CSVs on 'property_name' and 'application_name'
merged_df = pd.merge(csv1, csv2, on=['property_name', 'application_name'], suffixes=('_csv1', '_csv2'), how='outer')

# Step 3: Compare the property_value columns from both CSVs
merged_df['property_value_diff'] = merged_df['property_value_csv1'] != merged_df['property_value_csv2']

# Step 4: Create a column to highlight differences
merged_df['comparison_result'] = merged_df['property_value_diff'].apply(
    lambda x: 'Different' if x else 'Same'
)

# Step 5: Save the result to a new CSV
merged_df.to_csv("comparison_output.csv", index=False)

print("Comparison is complete. The result is saved in 'comparison_output.csv'.")
