#!/usr/bin/env python3

import argparse
import re
import sys
import os
import pandas as pd
import requests
from typing import List, Tuple
from urllib.parse import urlparse
from pathlib import Path

def fetch_content(source: str) -> str:
    """Fetch content from URL or local file."""
    # Check if source is a file path
    if os.path.exists(source):
        print(f"Reading from file: {source}")
        try:
            with open(source, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {source}: {e}", file=sys.stderr)
            sys.exit(1)
    # Otherwise treat as URL
    elif source.startswith(('http://', 'https://')):
        print(f"Fetching from URL: {source}")
        try:
            response = requests.get(source, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching URL {source}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Error: '{source}' is neither a valid file path nor a URL", file=sys.stderr)
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

def source_to_filename(source: str) -> str:
    """Convert URL or file path to a safe filename by replacing special characters."""
    if os.path.exists(source):
        # For file paths, use the base filename
        base_name = Path(source).stem
        filename = re.sub(r'[^\w\-_\.]', '_', base_name)
    else:
        # For URLs, use domain and path
        parsed = urlparse(source)
        filename = parsed.netloc + parsed.path
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remove consecutive underscores and trim
    filename = re.sub(r'_+', '_', filename).strip('_')
    # Add .csv extension if not present
    if not filename.endswith('.csv'):
        filename += '.csv'
    return filename

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
    parser = argparse.ArgumentParser(description='Scan HTML/text content with regex patterns from URL or file')
    parser.add_argument('source', help='URL or file path to scan')
    parser.add_argument('output', nargs='?', help='CSV output filename (optional if using --source-as-filename)')
    parser.add_argument('pattern', help='Regex pattern to search for')
    parser.add_argument('--distinct', action='store_true', 
                       help='Return only unique/distinct rows based on capturing groups')
    parser.add_argument('--source-as-filename', '--url-as-filename', action='store_true',
                       help='Use sanitized source name as the output filename')
    
    args = parser.parse_args()
    
    # Determine output filename
    if args.source_as_filename:
        output_file = source_to_filename(args.source)
        print(f"Using source-based filename: {output_file}")
    elif args.output:
        output_file = args.output
    else:
        print("Error: Either provide output filename or use --source-as-filename flag", file=sys.stderr)
        sys.exit(1)
    
    content = fetch_content(args.source)
    
    print(f"Scanning with pattern: {args.pattern}")
    matches = scan_with_regex(content, args.pattern)
    
    print(f"Found {len(matches)} matches")
    
    df = create_dataframe(matches, output_file, args.pattern)
    
    if args.distinct:
        # Drop duplicates based on capturing group columns only (not csv_output_name or regex_pattern)
        capturing_cols = ['capturing_group_1', 'capturing_group_2', 
                         'capturing_group_3', 'capturing_group_4', 
                         'capturing_group_5']
        df = df.drop_duplicates(subset=capturing_cols)
        print(f"After removing duplicates: {len(df)} unique matches")
    
    df.to_csv(output_file, index=False)
    print(f"Results saved to: {output_file}")
    
    print("\nFirst few rows of results:")
    print(df.head())

if __name__ == '__main__':
    main()