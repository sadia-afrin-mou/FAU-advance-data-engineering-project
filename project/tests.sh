#!/bin/bash

set -e

echo "Setting up environment and running pipeline..."

# if python3 is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# if pip or pip3 is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "pip is required but not installed. Please install pip first."
    exit 1
fi

# virtual environment if it doesn't exist
if [ ! -d "../venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv ../venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source ../venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Change to the root directory
cd "$(dirname "$0")/.."

echo "=== Running All Tests ==="
echo ""

# Run all tests with verbose output
python -m pytest -v
echo ""
echo "=== Tests Complete ==="

