#!/bin/bash
# Deploy script for Lambda function

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==================================="
echo "Lambda Deployment Script"
echo "==================================="
echo ""

# Check if function name is provided or get from Terraform
if [ -z "$1" ]; then
    echo "Getting function name from Terraform..."
    FUNCTION_NAME=$(cd terraform && terraform output -raw lambda_function_name 2>/dev/null)
    if [ -z "$FUNCTION_NAME" ]; then
        FUNCTION_NAME="braintrust-conversation-lambda-dev"
        echo "Using default function name: $FUNCTION_NAME"
    else
        echo "Function name from Terraform: $FUNCTION_NAME"
    fi
else
    FUNCTION_NAME="$1"
    echo "Using provided function name: $FUNCTION_NAME"
fi

# Get AWS profile
AWS_PROFILE="${AWS_PROFILE:-sandbox}"
echo "Using AWS profile: $AWS_PROFILE"
echo ""

# Navigate to Lambda directory
echo "Step 1: Building Lambda function..."
cd lambda

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Build TypeScript
echo "Compiling TypeScript..."
npm run build

# Create deployment package
echo ""
echo "Step 2: Creating deployment package..."
cd dist

# Include node_modules in the zip
echo "Copying node_modules..."
cp -r ../node_modules .

echo "Creating function.zip..."
zip -rq ../function.zip .

cd ..
echo "✓ Package created: function.zip ($(du -h function.zip | cut -f1))"

# Deploy to Lambda
echo ""
echo "Step 3: Deploying to AWS Lambda..."
aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --zip-file fileb://function.zip \
    --profile "$AWS_PROFILE" \
    --no-cli-pager

echo ""
echo "==================================="
echo "✓ Deployment Complete!"
echo "==================================="
echo ""
echo "Test the function with:"
echo "  python ../client.py --function $FUNCTION_NAME --profile $AWS_PROFILE"
echo ""
