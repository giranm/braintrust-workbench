#!/usr/bin/env bash
set -euo pipefail

# Script to bootstrap a new Braintrust project from template

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored message
print_status() {
    echo -e "${GREEN}==>${NC} $1"
}

print_error() {
    echo -e "${RED}Error:${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

# Usage information
usage() {
    cat << EOF
Usage: $0 <project-name> <type>

Creates a new Braintrust demo project from template.

Arguments:
  project-name    Name of the new project (e.g., llm-evaluation)
  type           Project type: python | typescript | fullstack

Examples:
  $0 sentiment-eval python
  $0 chat-ui typescript
  $0 rag-system fullstack

EOF
    exit 1
}

# Check arguments
if [ $# -ne 2 ]; then
    print_error "Invalid number of arguments"
    usage
fi

PROJECT_NAME="$1"
PROJECT_TYPE="$2"

# Validate project type
if [[ ! "$PROJECT_TYPE" =~ ^(python|typescript|fullstack)$ ]]; then
    print_error "Invalid project type: $PROJECT_TYPE"
    echo "Must be one of: python, typescript, fullstack"
    exit 1
fi

# Validate project name
if [[ ! "$PROJECT_NAME" =~ ^[a-z0-9-]+$ ]]; then
    print_error "Invalid project name: $PROJECT_NAME"
    echo "Must contain only lowercase letters, numbers, and hyphens"
    exit 1
fi

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$ROOT_DIR/projects/template"
TARGET_DIR="$ROOT_DIR/projects/$PROJECT_NAME"

# Check if template exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    print_error "Template directory not found: $TEMPLATE_DIR"
    exit 1
fi

# Check if project already exists
if [ -d "$TARGET_DIR" ]; then
    print_error "Project already exists: $TARGET_DIR"
    exit 1
fi

print_status "Creating new $PROJECT_TYPE project: $PROJECT_NAME"

# Create project directory
mkdir -p "$TARGET_DIR"

# Copy template files
print_status "Copying template files..."
cp -r "$TEMPLATE_DIR"/* "$TARGET_DIR/"
cp "$TEMPLATE_DIR/.mise.toml" "$TARGET_DIR/"

# Copy docs directory
if [ -d "$TEMPLATE_DIR/docs" ]; then
    cp -r "$TEMPLATE_DIR/docs" "$TARGET_DIR/"
fi

# Customize based on project type
cd "$TARGET_DIR"

case "$PROJECT_TYPE" in
    python)
        print_status "Setting up Python project..."

        # Update .mise.toml for Python
        cat > .mise.toml << EOF
# mise configuration for $PROJECT_NAME
[tools]
python = "3.12"
"npm:uv" = "latest"

[env]
_.file = ".env"
EOF

        # Create Python project structure
        mkdir -p src tests

        # Create basic Python files
        cat > src/__init__.py << 'EOF'
"""$PROJECT_NAME - A Braintrust demo project."""

__version__ = "0.1.0"
EOF

        cat > src/main.py << 'EOF'
"""Main entry point for the application."""

import os
from braintrust import init_logger

# Initialize Braintrust logger
logger = init_logger(project="$PROJECT_NAME")


def main():
    """Main function."""
    print("Hello from $PROJECT_NAME!")
    logger.log(message="Application started")


if __name__ == "__main__":
    main()
EOF

        cat > tests/__init__.py << 'EOF'
"""Tests for $PROJECT_NAME."""
EOF

        cat > tests/test_main.py << 'EOF'
"""Tests for main module."""

from src.main import main


def test_main():
    """Test main function runs without error."""
    main()
EOF

        # Create pyproject.toml
        cat > pyproject.toml << EOF
[project]
name = "$PROJECT_NAME"
version = "0.1.0"
description = "A Braintrust demo project"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "braintrust>=0.0.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.3.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
EOF

        # Remove TypeScript files if they exist
        rm -f package.json tsconfig.json
        ;;

    typescript)
        print_status "Setting up TypeScript project..."

        # Update .mise.toml for TypeScript
        cat > .mise.toml << EOF
# mise configuration for $PROJECT_NAME
[tools]
node = "20"

[env]
_.file = ".env"
EOF

        # Create TypeScript project structure
        mkdir -p src

        # Create package.json
        cat > package.json << EOF
{
  "name": "$PROJECT_NAME",
  "version": "0.1.0",
  "description": "A Braintrust demo project",
  "main": "src/index.ts",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "vitest"
  },
  "dependencies": {
    "braintrust": "latest"
  },
  "devDependencies": {
    "@types/node": "^20",
    "tsx": "^4",
    "typescript": "^5",
    "vitest": "^1"
  }
}
EOF

        # Create tsconfig.json
        cat > tsconfig.json << EOF
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
EOF

        # Create basic TypeScript file
        cat > src/index.ts << 'EOF'
import { initLogger } from "braintrust";

// Initialize Braintrust logger
const logger = initLogger({ project: "$PROJECT_NAME" });

async function main() {
  console.log("Hello from $PROJECT_NAME!");
  logger.log({ message: "Application started" });
}

main().catch(console.error);
EOF

        # Remove Python files if they exist
        rm -f pyproject.toml
        rm -rf src/__pycache__
        ;;

    fullstack)
        print_status "Setting up fullstack project..."
        print_warning "Fullstack setup requires manual configuration"
        print_warning "Please set up both Python backend and TypeScript frontend"

        # Update .mise.toml for fullstack
        cat > .mise.toml << EOF
# mise configuration for $PROJECT_NAME (fullstack)
[tools]
python = "3.12"
node = "20"
"npm:uv" = "latest"

[env]
_.file = ".env"
EOF

        mkdir -p backend frontend
        print_warning "Created backend/ and frontend/ directories"
        print_warning "Copy template contents into each as needed"
        ;;
esac

# Create .env.example
cat > .env.example << 'EOF'
# Braintrust API Key
# Get your key from: https://www.braintrust.dev/
BRAINTRUST_API_KEY=your-braintrust-api-key-here

# LLM Provider API Keys (as needed)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
EOF

# Update README with project name
sed -i.bak "s/\[Project Name\]/$PROJECT_NAME/g" README.md && rm README.md.bak

# Update CLAUDE.md with project name
sed -i.bak "s/\[Project Name\]/$PROJECT_NAME/g" CLAUDE.md && rm CLAUDE.md.bak

# Update docs files with project name
if [ -d "docs" ]; then
    for doc_file in docs/*.md; do
        if [ -f "$doc_file" ]; then
            sed -i.bak "s/\[Project Name\]/$PROJECT_NAME/g" "$doc_file" && rm "${doc_file}.bak"
            sed -i.bak "s/\[project-name\]/$PROJECT_NAME/g" "$doc_file" && rm "${doc_file}.bak"
        fi
    done
fi

print_status "Project created successfully!"
echo ""
echo "Next steps:"
echo ""
echo "  cd projects/$PROJECT_NAME"
echo "  mise install          # Install project tools"
echo "  mise trust            # Trust the .mise.toml config"
echo ""

if [ "$PROJECT_TYPE" = "python" ]; then
    echo "  uv sync               # Install Python dependencies"
    echo "  cp .env.example .env  # Configure environment"
    echo "  uv run python src/main.py"
elif [ "$PROJECT_TYPE" = "typescript" ]; then
    echo "  npm install           # Install Node dependencies"
    echo "  cp .env.example .env  # Configure environment"
    echo "  npm run dev"
fi

echo ""
print_status "Don't forget to add your Braintrust API key to .env!"
