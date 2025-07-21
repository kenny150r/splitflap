#!/bin/bash

# deploy_test.sh - Deploy Hall sensor test script to Pi Pico W using mpremote
# Make sure your Pi Pico W is connected

echo "Deploying Hall sensor test script to Pi Pico W using mpremote..."

# Check if mpremote is installed
if ! command -v mpremote &> /dev/null; then
    echo "Error: mpremote not found. Please install it first:"
    echo "pip install mpremote"
    exit 1
fi

# Check if test_hall.py exists
if [ ! -f "test_hall.py" ]; then
    echo "Error: test_hall.py not found in current directory"
    exit 1
fi

echo "Copying test_hall.py to Pi Pico W..."
mpremote cp test_hall.py :

if [ $? -eq 0 ]; then
    echo "Success! test_hall.py deployed to Pi Pico W"
    echo ""
    echo "Opening interactive shell..."
    echo "To run the test, type: exec(open('test_hall.py').read())"
    echo "Or press Ctrl+D to exit and run: mpremote run test_hall.py"
    echo "-" * 50
    mpremote
else
    echo "Error: Failed to deploy test_hall.py"
    exit 1
fi 