#!/bin/bash

# Fixed version that handles CSV files without trailing newline

CSV_FILE="${1:-jobs.csv}"

if [ ! -f "$CSV_FILE" ]; then
    echo "Error: File $CSV_FILE not found"
    exit 1
fi

echo "Processing CSV: $CSV_FILE"
echo "======================================"

# Skip header and process all lines (including last line without newline)
tail -n +2 "$CSV_FILE" | while IFS=',' read -r url regex || [ -n "$url" ]; do
    # Remove quotes from regex if present
    regex="${regex%\"}"
    regex="${regex#\"}"
    
    echo "Processing: $url"
    python html_scanner.py "$url" "$regex" --source-as-filename
done

echo "======================================"
echo "Processing complete!"