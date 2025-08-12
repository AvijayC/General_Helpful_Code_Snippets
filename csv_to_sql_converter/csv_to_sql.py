#!/usr/bin/env python3
"""
CSV to SQL Query Generator

This script reads a CSV file and generates a SQL query with UNION ALL statements.
Each row becomes a SELECT statement with all values as VARCHAR literals.
"""

import csv
import os
import sys
from pathlib import Path


def escape_sql_string(value):
    """Escape single quotes in SQL string values."""
    if value is None:
        return 'NULL'
    # Convert to string and escape single quotes
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def csv_to_sql_query(csv_path):
    """
    Convert CSV file to SQL query with UNION ALL statements.
    
    Args:
        csv_path (str): Path to the CSV file
        
    Returns:
        str: SQL query string
    """
    csv_file = Path(csv_path)
    
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Generate output filename
    output_file = csv_file.parent / f"{csv_file.stem}_query.sql"
    
    query_lines = []
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        
        # Read header row
        headers = next(csv_reader, None)
        if not headers:
            raise ValueError("CSV file is empty or has no headers")
        
        # Clean headers (remove spaces, special chars for SQL compatibility)
        clean_headers = [header.strip().replace(' ', '_').replace('-', '_') for header in headers]
        
        first_row = True
        
        for row in csv_reader:
            # Pad row with empty strings if it's shorter than headers
            while len(row) < len(headers):
                row.append('')
            
            # Truncate row if it's longer than headers
            row = row[:len(headers)]
            
            # Create SELECT statement
            select_values = []
            for i, value in enumerate(row):
                escaped_value = escape_sql_string(value)
                select_values.append(f"{escaped_value} AS {clean_headers[i]}")
            
            select_statement = f"SELECT {', '.join(select_values)}"
            
            if first_row:
                query_lines.append(select_statement)
                first_row = False
            else:
                query_lines.append(f"UNION ALL\n{select_statement}")
    
    if not query_lines:
        raise ValueError("No data rows found in CSV file")
    
    # Join all statements
    full_query = '\n'.join(query_lines) + ';'
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as output:
        output.write(full_query)
    
    return str(output_file)


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 2:
        print("Usage: python csv_to_sql.py <csv_file_path>")
        print("Example: python csv_to_sql.py data.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    try:
        output_file = csv_to_sql_query(csv_path)
        print(f"SQL query generated successfully: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()