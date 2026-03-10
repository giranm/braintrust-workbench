#!/bin/bash
# Helper script to load .env file and run terraform commands

set -e

# Check if .env exists in parent directory
if [ ! -f "../.env" ]; then
    echo "Error: .env file not found in parent directory"
    echo "Please create .env from .env.example and configure it"
    exit 1
fi

# Load .env file (export all variables)
echo "Loading environment variables from .env..."
set -a
source ../.env
set +a

# Run terraform command passed as arguments
if [ $# -eq 0 ]; then
    echo "Usage: ./load-env.sh <terraform-command>"
    echo "Examples:"
    echo "  ./load-env.sh plan"
    echo "  ./load-env.sh apply"
    echo "  ./load-env.sh output"
    exit 1
fi

echo "Running: terraform $@"
terraform "$@"
