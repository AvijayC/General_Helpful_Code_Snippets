#!/bin/bash

# Method 1: Simple bash loop reading CSV
echo "Method 1: Bash while loop"
while IFS=, read -r url output pattern; do
    # Skip header
    if [ "$url" != "url" ]; then
        echo "Processing: $output"
        python html_scanner.py "$url" "$output" "$pattern"
    fi
done < example_jobs.csv

# Method 2: Using xargs for parallel execution
echo -e "\nMethod 2: Parallel execution with xargs"
tail -n +2 example_jobs.csv | while IFS=, read -r url output pattern; do
    echo "python html_scanner.py '$url' '$output' '$pattern'"
done | xargs -P 4 -I {} sh -c '{}'

# Method 3: Using GNU parallel (if installed)
# parallel -j 4 --colsep ',' python html_scanner.py {1} {2} {3} :::: <(tail -n +2 example_jobs.csv)