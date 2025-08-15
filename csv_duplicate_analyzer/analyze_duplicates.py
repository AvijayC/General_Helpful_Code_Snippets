#!/usr/bin/env python3
"""
CSV Duplicate Row Analyzer

This script analyzes a CSV file to find differences between rows that have 
the same value in a specified column. It's designed to help understand why 
duplicate rows exist in SQL query outputs.
"""

import csv
import sys
from collections import defaultdict
from typing import List, Dict, Any
import argparse


def read_csv_with_duplicate_columns(filepath: str) -> tuple[List[str], List[Dict[int, Any]]]:
    """
    Read CSV file allowing for duplicate column names.
    Returns original headers and rows as list of dictionaries with column indices as keys.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)
        
        rows = []
        for row in reader:
            row_dict = {i: value for i, value in enumerate(row)}
            rows.append(row_dict)
    
    return headers, rows


def find_column_index(headers: List[str], column_name: str) -> int:
    """
    Find the first occurrence of a column name in headers.
    """
    try:
        return headers.index(column_name)
    except ValueError:
        raise ValueError(f"Column '{column_name}' not found in CSV headers")


def group_rows_by_column(rows: List[Dict[int, Any]], column_index: int) -> Dict[str, List[Dict[int, Any]]]:
    """
    Group rows by the value in the specified column index.
    """
    grouped = defaultdict(list)
    for row in rows:
        key_value = row.get(column_index, '')
        grouped[key_value].append(row)
    return dict(grouped)


def find_differences(rows: List[Dict[int, Any]], headers: List[str]) -> Dict[int, set]:
    """
    Find which columns have different values across the given rows.
    Returns a dictionary mapping column index to the set of unique values found.
    """
    differences = {}
    
    if len(rows) <= 1:
        return differences
    
    for col_idx in range(len(headers)):
        values = set()
        for row in rows:
            values.add(row.get(col_idx, ''))
        
        if len(values) > 1:
            differences[col_idx] = values
    
    return differences


def format_output(grouped_data: Dict[str, List[Dict[int, Any]]], headers: List[str], key_column_name: str):
    """
    Format and print the analysis results.
    """
    print(f"\n{'='*80}")
    print(f"Analysis of duplicates based on column: '{key_column_name}'")
    print(f"{'='*80}\n")
    
    total_groups = len(grouped_data)
    groups_with_duplicates = sum(1 for rows in grouped_data.values() if len(rows) > 1)
    
    print(f"Total unique values in '{key_column_name}': {total_groups}")
    print(f"Values with duplicate rows: {groups_with_duplicates}")
    print()
    
    for key_value, rows in grouped_data.items():
        if len(rows) > 1:
            print(f"\n{'-'*60}")
            print(f"Value '{key_value}' has {len(rows)} duplicate rows")
            print(f"{'-'*60}")
            
            differences = find_differences(rows, headers)
            
            if differences:
                print("\nColumns with differences:")
                for col_idx, values in differences.items():
                    col_name = headers[col_idx]
                    print(f"\n  Column: '{col_name}' (index {col_idx})")
                    print(f"  Unique values found:")
                    for value in sorted(values, key=str):
                        if value == '':
                            print(f"    - <empty>")
                        else:
                            print(f"    - {value}")
                
                print("\nDetailed row comparison:")
                for i, row in enumerate(rows, 1):
                    print(f"\n  Row {i}:")
                    for col_idx in differences:
                        col_name = headers[col_idx]
                        value = row.get(col_idx, '')
                        if value == '':
                            print(f"    {col_name}: <empty>")
                        else:
                            print(f"    {col_name}: {value}")
            else:
                print("\n  All columns are identical across duplicate rows!")
                print("  These are true duplicate rows with no differences.")
    
    if groups_with_duplicates == 0:
        print(f"\nNo duplicate rows found for column '{key_column_name}'")
        print("Each value in this column appears exactly once.")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze CSV file to find differences between duplicate rows based on a key column'
    )
    parser.add_argument('csv_file', help='Path to the CSV file to analyze')
    parser.add_argument('key_column', help='Name of the column to use as the key for grouping rows')
    parser.add_argument('--summary-only', action='store_true', 
                       help='Show only summary statistics without detailed differences')
    
    args = parser.parse_args()
    
    try:
        print(f"Reading CSV file: {args.csv_file}")
        headers, rows = read_csv_with_duplicate_columns(args.csv_file)
        
        print(f"Found {len(headers)} columns and {len(rows)} rows")
        
        column_index = find_column_index(headers, args.key_column)
        print(f"Using column '{args.key_column}' at index {column_index}")
        
        grouped_data = group_rows_by_column(rows, column_index)
        
        if args.summary_only:
            print(f"\n{'='*80}")
            print(f"Summary for column: '{args.key_column}'")
            print(f"{'='*80}\n")
            
            total_groups = len(grouped_data)
            groups_with_duplicates = sum(1 for rows in grouped_data.values() if len(rows) > 1)
            
            print(f"Total unique values: {total_groups}")
            print(f"Values with duplicate rows: {groups_with_duplicates}")
            
            if groups_with_duplicates > 0:
                print("\nDuplicate counts:")
                for key_value, rows in grouped_data.items():
                    if len(rows) > 1:
                        print(f"  '{key_value}': {len(rows)} rows")
        else:
            format_output(grouped_data, headers, args.key_column)
    
    except FileNotFoundError:
        print(f"Error: File '{args.csv_file}' not found")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        print(f"\nAvailable columns in the CSV:")
        try:
            headers, _ = read_csv_with_duplicate_columns(args.csv_file)
            for i, header in enumerate(headers):
                print(f"  {i}: {header}")
        except:
            pass
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()