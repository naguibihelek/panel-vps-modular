#!/bin/bash

# Setup GitHub Remote for Panel VPS Modular Repository
# This script helps you connect the local repository to GitHub

echo "=== GitHub Remote Setup Script ==="
echo

# Check if we're in the right directory
if [ ! -d ".git" ]; then
    echo "Error: Not in a git repository. Please run from /root/panel-vps-modular/"
    exit 1
fi

# Check current remotes
echo "Current remotes:"
git remote -v
echo

# Function to add remote
add_remote() {
    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/panel-vps-modular.git): " REPO_URL
    
    if [ -z "$REPO_URL" ]; then
        echo "Error: Repository URL cannot be empty"
        exit 1
    fi
    
    # Remove existing origin if it exists
    git remote remove origin 2>/dev/null
    
    # Add new origin
    git remote add origin "$REPO_URL"
    echo "Remote 'origin' added: $REPO_URL"
}

# Function to push branches
push_branches() {
    echo
    echo "Pushing branches to GitHub..."
    
    # Push main branch
    echo "Pushing main branch..."
    git push -u origin main
    
    # Push develop branch
    echo "Pushing develop branch..."
    git push -u origin develop
    
    # Push develop-core-foundation branch
    echo "Pushing develop-core-foundation branch..."
    git push -u origin develop-core-foundation
    
    echo
    echo "All branches pushed successfully!"
}

# Main flow
echo "This script will:"
echo "1. Add GitHub as remote origin"
echo "2. Push all branches (main, develop, develop-core-foundation)"
echo

read -p "Continue? (y/n): " CONTINUE

if [ "$CONTINUE" != "y" ]; then
    echo "Setup cancelled"
    exit 0
fi

# Add remote
add_remote

# Verify remote was added
echo
echo "New remotes:"
git remote -v
echo

# Push branches
read -p "Push all branches to GitHub? (y/n): " PUSH

if [ "$PUSH" = "y" ]; then
    push_branches
else
    echo
    echo "Branches not pushed. You can push manually with:"
    echo "  git push -u origin main"
    echo "  git push -u origin develop"
    echo "  git push -u origin develop-core-foundation"
fi

echo
echo "=== Setup Complete ==="
echo
echo "Next steps:"
echo "1. Create module branches: git checkout -b develop-vps-management"
echo "2. Implement modules following the architecture"
echo "3. Create PRs from module branches to develop"
echo "4. Merge develop to main when ready for production"