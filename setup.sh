#!/bin/bash

# Function to find Python command
find_python_cmd() {
    if command -v python3 &>/dev/null; then
        echo "python3"
    elif command -v python &>/dev/null; then
        echo "python"
    else
        echo "Python is not installed. Please install Python to use this script." >&2
        exit 1
    fi
}

# Function to find pip command
find_pip_cmd() {
    local python_cmd=$(find_python_cmd)

    if $python_cmd -m pip --version &>/dev/null; then
        echo "$python_cmd -m pip"
    else
        echo "pip is not installed. Please install pip to use this script." >&2
        exit 1
    fi
}

# Set Python and pip commands
PYTHON_CMD=$(find_python_cmd)
PIP_CMD=$(find_pip_cmd)

# Install Python backend dependencies
cd backend
$PIP_CMD install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install Python dependencies." >&2
    exit 1
fi
cd ..

# Install Node.js frontend dependencies
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "Failed to install Node.js dependencies." >&2
    exit 1
fi
cd ..

echo "Setup completed successfully."
