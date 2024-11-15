#!/bin/bash

# Run main.py
echo "Running automated script..."
python3 main.py

# Check if main.py executed successfully
if [ $? -eq 0 ]; then
    echo "main.py executed successfully"
    
    # Run benchmark.py
    echo "Running benchmark.py..."
    python3 benchmark.py

    # Check if benchmark.py executed successfully
    if [ $? -eq 0 ]; then
        echo "benchmark.py executed successfully"
        echo "Automation is complete."
    else
        echo "Error: benchmark.py failed to execute."
        exit 1
    fi
else
    echo "Error: main.py failed to execute. Skipping test.py."
    exit 1
fi