#!/usr/bin/env python3

import argparse
import re
import sys
import pandas as pd
import requests
from typing import List, Dict, Union, Any

def fetch_html_content(url: str) -> str:
    """Fetch HTML content from the given URL."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}", file=sys.stderr)
        sys.exit(1)

def scan_with_regex(html_content: str, pattern: str) -> tuple[List[Any], List[str], bool]:
    """
    Scan HTML content with the given regex pattern.
    Returns: (matches, group_names, has_named_groups)
    """
    try:
        compiled_pattern = re.compile(pattern)
        
        # Check if pattern has named groups
        group_names = list(compiled_pattern.groupindex.keys())
        has_named_groups = bool(group_names)
        
        # Find all matches
        matches_raw = compiled_pattern.finditer(html_content)
        matches = []
        
        for match in matches_raw:
            if has_named_groups:
                # Use named groups
                match_dict = match.groupdict()
                matches.append(match_dict)
            else:
                # Use numbered groups (including group 0 which is the full match)
                groups = match.groups()
                if groups:
                    matches.append(groups)
                else:
                    # No groups, just the full match
                    matches.append((match.group(0),))
        
        # If no named groups, create generic column names
        if not has_named_groups and matches:
            # Determine number of groups from first match
            num_groups = len(matches[0])
            group_names = [f'capturing_group_{i+1}' for i in range(num_groups)]
        
        return matches, group_names, has_named_groups
            
    except re.error as e:
        print(f"Invalid regex pattern: {e}", file=sys.stderr)
        sys.exit(1)

def create_dataframe(matches: List[Union[Dict, tuple]], 
                    group_names: List[str], 
                    has_named_groups: bool,
                    csv_name: str, 
                    pattern: str) -> pd.DataFrame:
    """Create a DataFrame from the matches with dynamic columns."""
    
    # Base columns
    base_columns = ['csv_output_name', 'regex_pattern']
    
    if not matches:
        # No matches found, return empty DataFrame with base columns and group columns
        all_columns = base_columns + group_names if group_names else base_columns
        return pd.DataFrame(columns=all_columns)
    
    data = []
    
    for match in matches:
        row = [csv_name, pattern]
        
        if has_named_groups:
            # Named groups - add values in order of group_names
            for name in group_names:
                row.append(match.get(name))
        else:
            # Numbered groups - add all captured groups
            for group_value in match:
                row.append(group_value)
        
        data.append(row)
    
    # Create column names
    all_columns = base_columns + group_names
    
    return pd.DataFrame(data, columns=all_columns)

def main():
    parser = argparse.ArgumentParser(
        description='Scan HTML content with regex patterns (supports named groups)',
        epilog='''
        Examples:
          # With named groups:
          python html_scanner_dynamic.py "https://example.com" "output.csv" "(?P<before>.{0,25})(?P<variable>variable_(?P<digit>\d)_value)(?P<after>.{0,25})"
          
          # With numbered groups:
          python html_scanner_dynamic.py "https://example.com" "output.csv" "(.{0,25})(variable_\d_value)(.{0,25})"
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('url', help='HTML URL to scan')
    parser.add_argument('output', help='CSV output filename')
    parser.add_argument('pattern', help='Regex pattern to search for (supports named groups)')
    parser.add_argument('--show-pattern', action='store_true', 
                       help='Display the pattern analysis before scanning')
    
    args = parser.parse_args()
    
    if args.show_pattern:
        print(f"Pattern: {args.pattern}")
        try:
            p = re.compile(args.pattern)
            if p.groupindex:
                print(f"Named groups found: {list(p.groupindex.keys())}")
            else:
                print("Using numbered capturing groups")
        except re.error as e:
            print(f"Pattern error: {e}")
            sys.exit(1)
        print()
    
    print(f"Fetching HTML from: {args.url}")
    html_content = fetch_html_content(args.url)
    
    print(f"Scanning with pattern: {args.pattern}")
    matches, group_names, has_named_groups = scan_with_regex(html_content, args.pattern)
    
    print(f"Found {len(matches)} matches")
    
    if has_named_groups:
        print(f"Using named groups: {group_names}")
    else:
        print(f"Using {len(group_names)} capturing groups")
    
    df = create_dataframe(matches, group_names, has_named_groups, args.output, args.pattern)
    
    df.to_csv(args.output, index=False)
    print(f"\nResults saved to: {args.output}")
    
    print(f"\nColumns in output: {list(df.columns)}")
    
    print("\nFirst few rows of results:")
    print(df.head())
    
    # Show a sample of the data in a more readable format if it's wide
    if len(df.columns) > 5 and len(df) > 0:
        print("\nFirst match details:")
        for col in df.columns:
            value = df.iloc[0][col]
            if pd.notna(value) and value != '':
                # Truncate long values for display
                display_value = str(value)[:50] + '...' if len(str(value)) > 50 else value
                print(f"  {col}: {display_value}")

if __name__ == '__main__':
    main()