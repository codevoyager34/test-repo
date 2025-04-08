#!/bin/bash

# === Configuration ===
CSV_FILE="replacements.csv"
INPUT_FILE="input.sql"
OUTPUT_FILE="output.sql"

# === Setup ===
cp "$INPUT_FILE" "$OUTPUT_FILE"
echo "📥 Starting replacements from $CSV_FILE..."
echo "Applying replacements to $INPUT_FILE → $OUTPUT_FILE"
echo "==============================================="

# === Loop through CSV and apply replacements ===
while IFS=, read -r find1 replace1 find2 replace2; do
  # Replace 1 (Column 1 → Column 2)
  if [[ -n "$find1" && -n "$replace1" ]]; then
    echo "🔁 Replacing '$find1' → '$replace1'"
    sed -i '' "s/${find1}/${replace1}/g" "$OUTPUT_FILE"
  fi

  # Replace 2 (Column 3 → Column 4)
  if [[ -n "$find2" && -n "$replace2" ]]; then
    echo "🔁 Replacing '$find2' → '$replace2'"
    sed -i '' "s/${find2}/${replace2}/g" "$OUTPUT_FILE"
  fi
done < "$CSV_FILE"

echo "✅ Done. Output written to $OUTPUT_FILE"
