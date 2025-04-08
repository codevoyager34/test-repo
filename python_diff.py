import csv

def load_replacements(csv_path):
    replacements = {}
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 2 and row[0] and row[1]:
                replacements[row[0]] = row[1]
            if len(row) >= 4 and row[2] and row[3]:
                replacements[row[2]] = row[3]
    return replacements

def apply_replacements(text, replacements):
    for find, replace in replacements.items():
        count = text.count(find)
        if count > 0:
            print(f"🔁 Replacing '{find}' → '{replace}' ({count} time{'s' if count > 1 else ''})")
        text = text.replace(find, replace)
    return text

def process_file(csv_path, input_sql_path, output_sql_path):
    print("📥 Loading replacements from:", csv_path)
    replacements = load_replacements(csv_path)

    print("📄 Reading SQL file:", input_sql_path)
    with open(input_sql_path, mode='r', encoding='utf-8') as f:
        sql_data = f.read()

    print("⚙️ Applying replacements...\n")
    modified_sql = apply_replacements(sql_data, replacements)

    print("\n💾 Writing output to:", output_sql_path)
    with open(output_sql_path, mode='w', encoding='utf-8') as f:
        f.write(modified_sql)

    print("✅ All done!")

# Example usage:
# process_file("replacements.csv", "input.sql", "output.sql")
