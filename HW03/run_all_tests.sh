#!/bin/bash

echo "================================================================="
echo "  Running Performance Tests with Multiple File Sizes"
echo "  Homework 03 - Nicolas Leone (1986354)"
echo "================================================================="
echo ""

# Array of test files
test_files=("testfile_1MB.bin" "testfile_5MB.bin" "testfile_10MB.bin" "testfile_50MB.bin" "testfile_100MB.bin")

# Run tests for each file size
for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        echo "Testing with $file..."
        ./HW03 "$file"
        echo ""
        echo "-----------------------------------------------------------------"
        echo ""
    else
        echo "Warning: $file not found, skipping..."
    fi
done

echo "================================================================="
echo "  All tests completed!"
echo "================================================================="
echo ""
echo "Results files generated:"
ls -lh results_*.csv 2>/dev/null

echo ""
echo "Now generating combined charts..."
python3 generate_charts_multi.py
