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
  type           Project type: python | typescript | fullstack | custom

Examples:
  $0 sentiment-eval python
  $0 chat-ui typescript
  $0 rag-system fullstack
  $0 my-experiment custom

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
if [[ ! "$PROJECT_TYPE" =~ ^(python|typescript|fullstack|custom)$ ]]; then
    print_error "Invalid project type: $PROJECT_TYPE"
    echo "Must be one of: python, typescript, fullstack, custom"
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
TEMPLATE_DIR="$ROOT_DIR/projects/_template"
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
pnpm = "9"

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

        # Update .mise.toml for fullstack
        cat > .mise.toml << EOF
# mise configuration for $PROJECT_NAME (fullstack)
[tools]
python = "3.12"
node = "20"
pnpm = "9"
"npm:uv" = "latest"

[env]
_.file = ".env"
EOF

        # Create directories
        mkdir -p backend frontend

        # Copy Docker files and replace placeholders
        print_status "Setting up Docker configuration..."

        # Copy and update docker-compose.yml (replace {{project-name}} placeholder)
        sed "s/{{project-name}}/$PROJECT_NAME/g" docker-compose.yml > docker-compose.yml.tmp
        mv docker-compose.yml.tmp docker-compose.yml

        # Copy and update Makefile (replace both {{Project Name}} and {{project-name}})
        # First replace {{Project Name}} with title case version
        PROJECT_TITLE=$(echo "$PROJECT_NAME" | tr '-' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')
        sed "s/{{Project Name}}/$PROJECT_TITLE/g" Makefile > Makefile.tmp
        mv Makefile.tmp Makefile
        sed "s/{{project-name}}/$PROJECT_NAME/g" Makefile > Makefile.tmp
        mv Makefile.tmp Makefile
        chmod +x Makefile

        # Copy and update .env.example (replace {{project-name}} placeholder)
        sed "s/{{project-name}}/$PROJECT_NAME/g" .env.example > .env.example.tmp
        mv .env.example.tmp .env.example

        # Dockerfile.backend, Dockerfile.frontend, .dockerignore are already copied from template
        # No placeholders to replace in these files

        print_status "Setting up backend (Python)..."
        cd backend

        # Create Python project structure
        mkdir -p src tests

        cat > src/__init__.py << 'PYEOF'
"""$PROJECT_NAME backend - A Braintrust demo project."""

__version__ = "0.1.0"
PYEOF

        cat > src/main.py << 'PYEOF'
"""Main entry point for the backend API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from braintrust import init_logger

# Initialize Braintrust logger
logger = init_logger(project="$PROJECT_NAME")

app = FastAPI(title="$PROJECT_NAME API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint."""
    logger.log(message="Root endpoint accessed")
    return {"message": "Hello from $PROJECT_NAME backend!"}

@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
PYEOF

        cat > tests/__init__.py << 'PYEOF'
"""Tests for $PROJECT_NAME backend."""
PYEOF

        cat > tests/test_main.py << 'PYEOF'
"""Tests for main API module."""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    """Test health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
PYEOF

        # Create pyproject.toml for backend
        cat > pyproject.toml << PYEOF
[project]
name = "$PROJECT_NAME"
version = "0.1.0"
description = "Backend for $PROJECT_NAME - A Braintrust demo project"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "braintrust>=0.0.1",
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.26.0",
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
PYEOF

        cd ..

        print_status "Setting up frontend (Next.js + TypeScript)..."
        cd frontend

        # Create package.json for Next.js frontend
        cat > package.json << JSEOF
{
  "name": "$PROJECT_NAME-frontend",
  "version": "0.1.0",
  "description": "Frontend for $PROJECT_NAME - A Braintrust demo project",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "next": "^14"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "typescript": "^5"
  }
}
JSEOF

        # Create tsconfig.json for Next.js
        cat > tsconfig.json << 'JSEOF'
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
JSEOF

        # Create next.config.js
        cat > next.config.js << 'JSEOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig
JSEOF

        # Create Next.js app structure
        mkdir -p src/app public

        # Create root layout
        cat > src/app/layout.tsx << 'JSEOF'
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: '$PROJECT_NAME',
  description: 'A Braintrust demo project',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
JSEOF

        # Create main page
        cat > src/app/page.tsx << 'JSEOF'
'use client'

import { useState, useEffect } from 'react'
import styles from './page.module.css'

export default function Home() {
  const [message, setMessage] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(true)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    fetch(\`\${apiUrl}/\`)
      .then(res => res.json())
      .then(data => {
        setMessage(data.message)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching from backend:', err)
        setError('Failed to connect to backend')
        setLoading(false)
      })
  }, [])

  return (
    <main className={styles.main}>
      <h1 className={styles.title}>$PROJECT_NAME</h1>
      {loading && <p>Loading...</p>}
      {error && <p className={styles.error}>{error}</p>}
      {message && <p className={styles.message}>{message}</p>}
      <div className={styles.info}>
        <p>Frontend: Next.js + TypeScript</p>
        <p>Backend: FastAPI + Python</p>
        <p>Observability: Braintrust</p>
      </div>
    </main>
  )
}
JSEOF

        # Create page styles
        cat > src/app/page.module.css << 'JSEOF'
.main {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 2rem;
}

.title {
  font-size: 3rem;
  margin-bottom: 2rem;
  text-align: center;
}

.message {
  font-size: 1.5rem;
  margin: 1rem 0;
  color: #0070f3;
}

.error {
  font-size: 1.25rem;
  margin: 1rem 0;
  color: #ff0000;
}

.info {
  margin-top: 2rem;
  padding: 1rem;
  border: 1px solid #eaeaea;
  border-radius: 8px;
  text-align: center;
}

.info p {
  margin: 0.5rem 0;
}
JSEOF

        # Create global styles
        cat > src/app/globals.css << 'JSEOF'
:root {
  --max-width: 1100px;
  --font-mono: ui-monospace, Menlo, Monaco, 'Cascadia Mono', 'Segoe UI Mono',
    'Roboto Mono', 'Oxygen Mono', 'Ubuntu Monospace', 'Source Code Pro',
    'Fira Mono', 'Droid Sans Mono', 'Courier New', monospace;
}

* {
  box-sizing: border-box;
  padding: 0;
  margin: 0;
}

html,
body {
  max-width: 100vw;
  overflow-x: hidden;
}

body {
  font-family: var(--font-mono);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: inherit;
  text-decoration: none;
}
JSEOF

        # Create public directory with .gitkeep
        touch public/.gitkeep

        cd ..

        print_status "Fullstack project created with Docker support!"
        print_status "Backend: Python/FastAPI, Frontend: Next.js/TypeScript"
        print_status "Use 'make help' to see available commands"
        ;;

    custom)
        print_status "Setting up custom project (blank canvas)..."

        # Create minimal structure - only docs directory
        mkdir -p docs

        # Copy docs templates from _template
        if [ -d "$TEMPLATE_DIR/docs" ]; then
            cp -r "$TEMPLATE_DIR/docs"/* docs/
            print_status "Created docs/ directory with templates"
        fi

        # Create minimal README
        cat > README.md << 'EOF'
# [Project Name]

[Brief description of what this project does]

## Overview

This is a custom Braintrust project with a blank canvas structure.

## Setup

[Document your setup steps here]

## Running

[Document how to run your project here]

## Documentation

See the `docs/` directory for:
- **[planning.md](./docs/planning.md)**: Project goals, scope, and implementation plan
- **[implementation.md](./docs/implementation.md)**: Technical decisions and progress
- **[issues.md](./docs/issues.md)**: Known issues and resolutions
- **[changelog.md](./docs/changelog.md)**: Version history

## Learn More

- **Braintrust Docs**: https://www.braintrust.dev/docs
- **Braintrust Cookbook**: https://github.com/braintrustdata/braintrust-cookbook
EOF

        # Create minimal AGENTS.md
        cat > AGENTS.md << 'EOF'
# AGENTS.md

This file is the source of truth for project-level agent guidance.

## Project overview

[Describe what this project demonstrates about Braintrust]

**Type**: Custom
**Focus**: [e.g., LLM Evaluation, Prompt Engineering, A/B Testing, etc.]

## Working context

This is a custom Braintrust project with minimal scaffolding. Keep it isolated,
runnable, and easy to understand as a standalone demo.

## Read order

Before non-trivial work:

1. This file
2. `README.md`
3. `docs/planning.md`
4. `docs/issues.md`
5. `docs/implementation.md`

## Project structure

```
[project-name]/
├── AGENTS.md           # Source of truth for agent guidance
├── CLAUDE.md           # Compatibility shim, if present
├── README.md           # Public documentation
└── docs/               # Development documentation
    ├── planning.md         # Project goals and strategy
    ├── implementation.md   # Technical decisions and notes
    ├── issues.md           # Bugs and known issues
    └── changelog.md        # Version history
```

## Working model

- Keep the project lean and docs-first until the user defines more structure.
- Reference Braintrust docs: https://www.braintrust.dev/docs
- Reference the cookbook: https://github.com/braintrustdata/braintrust-cookbook
- Keep `docs/` updated with decisions, issues, and changes.
EOF

        # Create minimal CLAUDE.md compatibility shim
        cat > CLAUDE.md << 'EOF'
# Claude Compatibility Note

`AGENTS.md` is the source of truth for project guidance in this project.

When working here with Claude:

1. Read `AGENTS.md` first.
2. Then follow `README.md` and `docs/` as directed there.

If this file and `AGENTS.md` ever disagree, follow `AGENTS.md`.
EOF

        # Update placeholders in copied files
        sed -i.bak "s/\[Project Name\]/${PROJECT_NAME//[-_]/ }/g" README.md && rm README.md.bak
        sed -i.bak "s/\[project-name\]/$PROJECT_NAME/g" README.md && rm README.md.bak

        sed -i.bak "s/\[Project Name\]/${PROJECT_NAME//[-_]/ }/g" AGENTS.md && rm AGENTS.md.bak
        sed -i.bak "s/\[project-name\]/$PROJECT_NAME/g" AGENTS.md && rm AGENTS.md.bak

        sed -i.bak "s/\[Project Name\]/${PROJECT_NAME//[-_]/ }/g" CLAUDE.md && rm CLAUDE.md.bak
        sed -i.bak "s/\[project-name\]/$PROJECT_NAME/g" CLAUDE.md && rm CLAUDE.md.bak

        # Update docs files with project name
        if [ -d "docs" ]; then
            for doc_file in docs/*.md; do
                if [ -f "$doc_file" ]; then
                    sed -i.bak "s/\[Project Name\]/${PROJECT_NAME//[-_]/ }/g" "$doc_file" && rm "${doc_file}.bak"
                    sed -i.bak "s/\[project-name\]/$PROJECT_NAME/g" "$doc_file" && rm "${doc_file}.bak"
                fi
            done
        fi

        print_status "Custom project created successfully!"
        print_status "This is a blank canvas - implement your own structure"
        ;;
esac

# Create .env.example (skip for custom projects)
if [ "$PROJECT_TYPE" != "custom" ]; then
    cat > .env.example << 'EOF'
# Braintrust API Key
# Get your key from: https://www.braintrust.dev/
BRAINTRUST_API_KEY=your-braintrust-api-key-here

# LLM Provider API Keys (as needed)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
EOF
fi

# Update README with project name (skip for custom - already done in case)
if [ "$PROJECT_TYPE" != "custom" ]; then
    sed -i.bak "s/\[Project Name\]/$PROJECT_NAME/g" README.md && rm README.md.bak
fi

# Update AGENTS.md with project name (skip for custom - already done in case)
if [ "$PROJECT_TYPE" != "custom" ]; then
    sed -i.bak "s/\[Project Name\]/$PROJECT_NAME/g" AGENTS.md && rm AGENTS.md.bak
fi

# Update CLAUDE.md with project name (skip for custom - already done in case)
if [ "$PROJECT_TYPE" != "custom" ]; then
    sed -i.bak "s/\[Project Name\]/$PROJECT_NAME/g" CLAUDE.md && rm CLAUDE.md.bak
fi

# Update docs files with project name (skip for custom - already done in case)
if [ "$PROJECT_TYPE" != "custom" ] && [ -d "docs" ]; then
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

if [ "$PROJECT_TYPE" = "fullstack" ]; then
    echo ""
    echo "Docker setup (recommended):"
    echo "  make setup            # Create .env file"
    echo "  # Edit .env with your API keys"
    echo "  make build            # Build Docker images"
    echo "  make up               # Start containers"
    echo "  make logs             # View logs"
    echo ""
    echo "Local setup (alternative):"
    echo "  mise install          # Install project tools"
    echo "  mise trust            # Trust the .mise.toml config"
    echo "  cd backend && uv sync # Install backend dependencies"
    echo "  cd frontend && pnpm install # Install frontend dependencies"
else
    echo "  mise install          # Install project tools"
    echo "  mise trust            # Trust the .mise.toml config"
    echo ""
    if [ "$PROJECT_TYPE" = "python" ]; then
        echo "  uv sync               # Install Python dependencies"
        echo "  cp .env.example .env  # Configure environment"
        echo "  uv run python src/main.py"
    elif [ "$PROJECT_TYPE" = "typescript" ]; then
        echo "  pnpm install          # Install Node dependencies"
        echo "  cp .env.example .env  # Configure environment"
        echo "  pnpm dev"
    elif [ "$PROJECT_TYPE" = "custom" ]; then
        echo "  # This is a blank canvas - set up your own structure"
        echo "  # Start by reviewing docs/planning.md"
        echo "  # Then implement your project as needed"
    fi
fi

echo ""
if [ "$PROJECT_TYPE" = "custom" ]; then
    print_status "Custom project created! Review docs/planning.md to get started."
else
    print_status "Don't forget to add your Braintrust API key to .env!"
fi
