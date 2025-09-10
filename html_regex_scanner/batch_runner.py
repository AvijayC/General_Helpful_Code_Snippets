#!/usr/bin/env python3

import csv
import subprocess
import sys
import argparse
from pathlib import Path

def run_batch_from_csv(csv_file: str, script: str = 'html_scanner.py', use_distinct: bool = False):
    """
    Run the HTML scanner script multiple times with arguments from a CSV file.
    
    CSV format expected:
    url,output_file,pattern
    https://example.com,output1.csv,"pattern1"
    https://site.com,output2.csv,"pattern2"
    """
    
    with open(csv_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=1):
            print(f"\n{'='*60}")
            print(f"Running job {row_num}: {row.get('output_file', row.get('output'))}")
            print(f"{'='*60}")
            
            # Build command
            cmd = [
                sys.executable,  # Use current Python interpreter
                script,
                row.get('url'),
                row.get('output_file', row.get('output')),  # Support both column names
                row.get('pattern')
            ]
            
            # Add optional flags
            if use_distinct:
                cmd.append('--distinct')
            
            # Add any extra flags from CSV if present
            if 'flags' in row and row['flags']:
                cmd.extend(row['flags'].split())
            
            try:
                # Run the command
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✓ Success: {row.get('output_file', row.get('output'))}")
                    if result.stdout:
                        print(result.stdout)
                else:
                    print(f"✗ Failed: {row.get('output_file', row.get('output'))}")
                    if result.stderr:
                        print(f"Error: {result.stderr}")
                        
            except Exception as e:
                print(f"✗ Exception running job {row_num}: {e}")
    
    print(f"\n{'='*60}")
    print("Batch processing complete!")
    print(f"{'='*60}")

def main():
    parser = argparse.ArgumentParser(
        description='Run HTML scanner multiple times from CSV input',
        epilog='''
        CSV Format Example:
        url,output_file,pattern
        https://example.com,output1.csv,"(.{0,25})(variable_\d_value)(.{0,25})"
        https://site.com,output2.csv,"(?P<content>\{\{[^}]*\}\})"
        
        Or create CSV programmatically:
        import csv
        with open('jobs.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['url', 'output_file', 'pattern'])
            writer.writerow(['https://example.com', 'out1.csv', 'pattern1'])
        '''
    )
    parser.add_argument('csv_file', help='CSV file with batch job arguments')
    parser.add_argument('--script', default='html_scanner.py', 
                       help='Scanner script to use (default: html_scanner.py)')
    parser.add_argument('--distinct', action='store_true',
                       help='Add --distinct flag to all runs')
    
    args = parser.parse_args()
    
    if not Path(args.csv_file).exists():
        print(f"Error: CSV file '{args.csv_file}' not found")
        sys.exit(1)
    
    if not Path(args.script).exists():
        print(f"Error: Script '{args.script}' not found")
        sys.exit(1)
    
    run_batch_from_csv(args.csv_file, args.script, args.distinct)

if __name__ == '__main__':
    main()