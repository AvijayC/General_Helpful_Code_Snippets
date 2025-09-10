# Shell Scripting Guide for HTML Scanner

## Table of Contents
1. [Basic One-Liners](#basic-one-liners)
2. [Understanding Shell Arguments](#understanding-shell-arguments)
3. [CSV Processing](#csv-processing)
4. [File and URL Processing](#file-and-url-processing)
5. [Advanced Techniques](#advanced-techniques)
6. [Shell Scripting Fundamentals](#shell-scripting-fundamentals)

---

## Basic One-Liners

### 1. Simple CSV Processing
```bash
tail -n +2 jobs.csv | while IFS=, read url regex; do python html_scanner.py "$url" "$regex" --source-as-filename; done
```

**Breakdown:**
- `tail -n +2 jobs.csv` - Skip first line (header) of CSV
  - `-n +2` means "start from line 2"
- `|` - Pipe operator, sends output to next command
- `while IFS=, read url regex` - Loop through each line
  - `IFS=,` - Internal Field Separator set to comma (for CSV)
  - `read url regex` - Split line into two variables
- `do ... done` - Loop body
- `"$url"` - Variable expansion with quotes (preserves spaces)

### 2. Handling Quoted CSV Fields
```bash
tail -n +2 jobs.csv | while IFS=, read url regex; do 
    regex="${regex%\"}"  # Remove trailing quote
    regex="${regex#\"}"  # Remove leading quote
    python html_scanner.py "$url" "$regex" --source-as-filename
done
```

**String Manipulation:**
- `${var%pattern}` - Remove shortest match of pattern from end
- `${var#pattern}` - Remove shortest match of pattern from beginning
- `${var%%pattern}` - Remove longest match from end
- `${var##pattern}` - Remove longest match from beginning

### 3. Processing Last Line Without Newline
```bash
while IFS=',' read -r url regex || [ -n "$url" ]; do
    if [ "$url" != "url" ]; then
        python html_scanner.py "$url" "$regex" --source-as-filename
    fi
done < jobs.csv
```

**Key Points:**
- `|| [ -n "$url" ]` - Process last line even without newline
- `[ -n "$url" ]` - Test if variable is non-empty
- `-r` in `read -r` - Prevent backslash interpretation

---

## Understanding Shell Arguments

### Positional Parameters
```bash
#!/bin/bash
# $0 - Script name
# $1 - First argument
# $2 - Second argument
# $# - Number of arguments
# $@ - All arguments as separate words
# $* - All arguments as single word

echo "Script: $0"
echo "First arg: $1"
echo "Total args: $#"
```

### Default Values
```bash
# Use default if variable is unset
CSV_FILE="${1:-jobs.csv}"  # If $1 is empty, use jobs.csv

# Check if variable is set
if [ -z "$CSV_FILE" ]; then
    echo "No file specified"
fi
```

---

## CSV Processing

### Method 1: While Loop
```bash
while IFS=',' read -r col1 col2 col3; do
    echo "Processing: $col1, $col2, $col3"
done < file.csv
```

### Method 2: AWK
```bash
awk -F',' '{print $1, $2}' file.csv
```

**AWK Breakdown:**
- `-F','` - Field separator is comma
- `$1, $2` - First and second columns
- `NR` - Row number
- `NF` - Number of fields

### Method 3: Cut Command
```bash
cut -d',' -f1,3 file.csv  # Extract columns 1 and 3
```

---

## File and URL Processing

### Processing List of Sources
```bash
# Single regex for multiple sources
PATTERN="(.{0,25})(variable_\d+_value)(.{0,25})"
while read source; do 
    python html_scanner.py "$source" "$PATTERN" --source-as-filename
done < sources.txt
```

### Parallel Processing with xargs
```bash
# Run 4 processes in parallel
cat sources.txt | xargs -P 4 -I {} sh -c 'python html_scanner.py "{}" "pattern" --source-as-filename'
```

**xargs Options:**
- `-P 4` - Run 4 processes in parallel
- `-I {}` - Replace {} with input
- `-n 1` - One argument per command

### Using GNU Parallel
```bash
parallel -j 4 python html_scanner.py {} "pattern" --source-as-filename :::: sources.txt
```

---

## Advanced Techniques

### 1. Progress Tracking
```bash
#!/bin/bash
i=1
total=$(wc -l < file.txt)
while read line; do
    echo "[$i/$total] Processing: $line"
    # Your command here
    ((i++))
done < file.txt
```

### 2. Error Handling
```bash
#!/bin/bash
set -e  # Exit on error
set -u  # Error on undefined variables
set -o pipefail  # Pipe failures cause script to fail

# Trap errors
trap 'echo "Error on line $LINENO"' ERR

# Check command success
if python script.py; then
    echo "Success"
else
    echo "Failed with code $?"
fi
```

### 3. Colored Output
```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Success${NC}"
echo -e "${RED}Error${NC}"
```

### 4. Functions
```bash
process_file() {
    local file="$1"
    local pattern="$2"
    echo "Processing $file with pattern $pattern"
    python html_scanner.py "$file" "$pattern" --source-as-filename
}

# Call function
process_file "test.html" "pattern"
```

---

## Shell Scripting Fundamentals

### Conditional Statements
```bash
# If statement
if [ -f "file.txt" ]; then
    echo "File exists"
elif [ -d "directory" ]; then
    echo "Directory exists"
else
    echo "Neither exists"
fi

# Test operators
# -f : File exists
# -d : Directory exists
# -z : String is empty
# -n : String is not empty
# -eq : Numbers are equal
# -ne : Numbers not equal
# -gt : Greater than
# -lt : Less than
```

### Loops
```bash
# For loop
for i in {1..5}; do
    echo "Number: $i"
done

# For loop over files
for file in *.txt; do
    echo "Processing $file"
done

# C-style for loop
for ((i=0; i<5; i++)); do
    echo "$i"
done

# While loop
counter=0
while [ $counter -lt 5 ]; do
    echo $counter
    ((counter++))
done
```

### Arrays
```bash
# Declare array
arr=("item1" "item2" "item3")

# Access elements
echo ${arr[0]}  # First element
echo ${arr[@]}  # All elements
echo ${#arr[@]} # Array length

# Loop through array
for item in "${arr[@]}"; do
    echo "$item"
done
```

### String Operations
```bash
str="hello world"

# Length
echo ${#str}

# Substring
echo ${str:0:5}  # "hello"

# Replace
echo ${str/world/universe}  # "hello universe"

# Upper/lowercase (bash 4+)
echo ${str^^}  # "HELLO WORLD"
echo ${str,,}  # "hello world"
```

### Process Substitution
```bash
# Compare two command outputs
diff <(ls dir1) <(ls dir2)

# Read from command output
while read line; do
    echo "$line"
done < <(ls -la)
```

### Useful Built-in Variables
```bash
$? - Exit status of last command
$$ - Current process ID
$! - PID of last background process
$- - Current shell options
$RANDOM - Random number
$LINENO - Current line number in script
$SECONDS - Seconds since script started
```

---

## Practical Examples

### 1. Batch Processing with Error Recovery
```bash
#!/bin/bash
FAILED_URLS=""

while IFS=',' read -r url regex || [ -n "$url" ]; do
    if [ "$url" = "url" ]; then continue; fi
    
    if python html_scanner.py "$url" "$regex" --source-as-filename; then
        echo "✓ Success: $url"
    else
        echo "✗ Failed: $url"
        FAILED_URLS="$FAILED_URLS$url\n"
    fi
done < jobs.csv

if [ -n "$FAILED_URLS" ]; then
    echo -e "\nFailed URLs:\n$FAILED_URLS"
fi
```

### 2. Dynamic Pattern Selection
```bash
#!/bin/bash
case "$1" in
    "emails")
        PATTERN='[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        ;;
    "urls")
        PATTERN='https?://[^\s<>"{}|\\^`\[\]]+'
        ;;
    "variables")
        PATTERN='variable_\d+_value'
        ;;
    *)
        echo "Usage: $0 {emails|urls|variables}"
        exit 1
        ;;
esac

while read source; do
    python html_scanner.py "$source" "$PATTERN" --source-as-filename
done < sources.txt
```

### 3. Recursive File Processing
```bash
#!/bin/bash
find . -name "*.html" -type f | while read file; do
    echo "Processing: $file"
    python html_scanner.py "$file" "pattern" --source-as-filename
done
```

### 4. Logging with Timestamps
```bash
#!/bin/bash
LOG_FILE="scanner_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting batch processing"
while read source; do
    log "Processing: $source"
    python html_scanner.py "$source" "pattern" --source-as-filename 2>&1 | tee -a "$LOG_FILE"
done < sources.txt
log "Batch processing complete"
```

---

## Tips and Best Practices

1. **Always quote variables**: `"$var"` not `$var`
2. **Use `shellcheck`**: Install and run `shellcheck script.sh` to find issues
3. **Set safety options**: Start scripts with `set -euo pipefail`
4. **Use meaningful variable names**: `SOURCE_FILE` not `sf`
5. **Add comments**: Explain complex logic
6. **Test with edge cases**: Empty files, spaces in names, special characters
7. **Use functions**: For repeated code blocks
8. **Handle errors gracefully**: Check return codes, use trap
9. **Validate input**: Check if files exist, arguments are provided
10. **Use proper shebang**: `#!/bin/bash` for bash-specific features

---

## Quick Reference Card

```bash
# Read CSV and process
tail -n +2 file.csv | while IFS=, read col1 col2; do ...; done

# Remove quotes
var="${var%\"}" && var="${var#\"}"

# Check file exists
[ -f "file" ] && echo "exists"

# Default value
VAR="${1:-default}"

# Loop with counter
i=0; while [ $i -lt 10 ]; do echo $i; ((i++)); done

# Parallel execution
cat list.txt | xargs -P 4 -I {} command {}

# String contains
[[ "$string" == *"substring"* ]] && echo "contains"

# Arithmetic
result=$((5 + 3))

# Command substitution
output=$(command)

# Process substitution
diff <(command1) <(command2)
```