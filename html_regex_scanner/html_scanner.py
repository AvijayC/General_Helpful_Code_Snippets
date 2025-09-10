#!/usr/bin/env python3

import argparse
import re
import sys
import pandas as pd
import requests
from typing import List, Tuple

def fetch_html_content(url: str) -> str:
    """Fetch HTML content from the given URL."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}", file=sys.stderr)
        sys.exit(1)

def scan_with_regex(html_content: str, pattern: str) -> List[Tuple]:
    """Scan HTML content with the given regex pattern."""
    try:
        compiled_pattern = re.compile(pattern)
        matches = compiled_pattern.findall(html_content)
        
        if not matches:
            return []
        
        if isinstance(matches[0], str):
            return [(match,) for match in matches]
        else:
            return matches
            
    except re.error as e:
        print(f"Invalid regex pattern: {e}", file=sys.stderr)
        sys.exit(1)

def create_dataframe(matches: List[Tuple], csv_name: str, pattern: str) -> pd.DataFrame:
    """Create a DataFrame from the matches."""
    if not matches:
        return pd.DataFrame(columns=['csv_output_name', 'regex_pattern', 
                                    'capturing_group_1', 'capturing_group_2', 
                                    'capturing_group_3', 'capturing_group_4', 
                                    'capturing_group_5'])
    
    data = []
    for match in matches:
        row = [csv_name, pattern]
        
        for i in range(5):
            if i < len(match):
                row.append(match[i])
            else:
                row.append(None)
        
        data.append(row)
    
    columns = ['csv_output_name', 'regex_pattern', 
               'capturing_group_1', 'capturing_group_2', 
               'capturing_group_3', 'capturing_group_4', 
               'capturing_group_5']
    
    return pd.DataFrame(data, columns=columns)

def main():
    parser = argparse.ArgumentParser(description='Scan HTML content with regex patterns')
    parser.add_argument('url', help='HTML URL to scan')
    parser.add_argument('output', help='CSV output filename')
    parser.add_argument('pattern', help='Regex pattern to search for')
    parser.add_argument('--distinct', action='store_true', 
                       help='Return only unique/distinct rows based on capturing groups')
    
    args = parser.parse_args()
    
    print(f"Fetching HTML from: {args.url}")
    html_content = fetch_html_content(args.url)
    
    print(f"Scanning with pattern: {args.pattern}")
    matches = scan_with_regex(html_content, args.pattern)
    
    print(f"Found {len(matches)} matches")
    
    df = create_dataframe(matches, args.output, args.pattern)
    
    if args.distinct:
        # Drop duplicates based on capturing group columns only (not csv_output_name or regex_pattern)
        capturing_cols = ['capturing_group_1', 'capturing_group_2', 
                         'capturing_group_3', 'capturing_group_4', 
                         'capturing_group_5']
        df = df.drop_duplicates(subset=capturing_cols)
        print(f"After removing duplicates: {len(df)} unique matches")
    
    df.to_csv(args.output, index=False)
    print(f"Results saved to: {args.output}")
    
    print("\nFirst few rows of results:")
    print(df.head())

if __name__ == '__main__':
    main()