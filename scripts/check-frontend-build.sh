#!/bin/bash
set -e

# Check if frontend source changed
if ! git diff --cached --name-only | grep -q "^src/frontend/"; then
    exit 0
fi

# Verify yarn is available
if ! command -v yarn &> /dev/null; then
    echo "ERROR: yarn is required but not installed."
    echo "Please install Node.js and yarn to commit frontend changes."
    exit 1
fi

echo "Frontend files changed, rebuilding..."
cd src/frontend && yarn build-for-backend

# Check if build output differs from staged version
if git diff --name-only -- src/hope/apps/web/static/web/ | grep -q .; then
    echo ""
    echo "ERROR: Frontend build output changed. Please stage the updated files:"
    git diff --stat -- src/hope/apps/web/static/web/
    echo ""
    echo "Run: git add src/hope/apps/web/static/web/"
    exit 1
fi

echo "Frontend build is up-to-date."
