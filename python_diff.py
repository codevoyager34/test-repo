import csv
import re

def load_replacements(csv_path):
    replacements = []
    with open(csv_path, mode='r', encoding='utf-8-sig', errors='replace') as f:
        cleaned_lines = (line.replace('\x00', '') for line in f)
        reader = csv.reader(cleaned_lines)
        for idx, row in enumerate(reader, start=1):
            if len(row) >= 2 and row[0].strip() and row[1].strip():
                replacements.append((row[0].strip(), row[1].strip()))
            if len(row) >= 4 and row[2].strip() and row[3].strip():
                replacements.append((row[2].strip(), row[3].strip()))
    return replacements

def apply_replacements(text, replacements):
    for find, replace in replacements:
        try:
            # Build a regex pattern that matches `find` literally (escaped)
            pattern = re.escape(find)
            # Replace all occurrences (global match)
            matches = re.findall(pattern, text)
            count = len(matches)
            if count > 0:
                print(f"🔁 Replacing '{find}' → '{replace}' ({count} time{'s' if count > 1 else ''})")
                text = re.sub(pattern, replace, text)
        except re.error as e:
            print(f"⚠️ Skipping pattern '{find}': Regex error - {e}")
    return text

def process_file(csv_path, input_sql_path, output_sql_path):
    print("📥 Loading replacements from:", csv_path)
    replacements = load_replacements(csv_path)

    print("📄 Reading SQL file:", input_sql_path)
    with open(input_sql_path, mode='r', encoding='utf-8-sig', errors='replace') as f:
        sql_data = f.read()

    print("⚙️ Applying replacements...\n")
    modified_sql = apply_replacements(sql_data, replacements)

    print("\n💾 Writing output to:", output_sql_path)
    with open(output_sql_path, mode='w', encoding='utf-8') as f:
        f.write(modified_sql)

    print("✅ All done!")

# Run it (edit these filenames as needed)
if __name__ == "__main__":
    process_file("replacements.csv", "input.sql", "output.sql")
