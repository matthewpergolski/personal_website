#!/bin/bash

# Define the base path
BASE_PATH="/Users/pergolicious/Scripts/personal_website/personal_website"

# Create main project directories
echo "Creating project directories..."
mkdir -p "$BASE_PATH"/app/static/{css,js,img}
mkdir -p "$BASE_PATH"/app/templates
mkdir -p "$BASE_PATH"/tests

# Create Python files
echo "Creating Python files..."
touch "$BASE_PATH"/app/__init__.py
touch "$BASE_PATH"/app/routes.py
touch "$BASE_PATH"/app/github_api.py
touch "$BASE_PATH"/tests/__init__.py
touch "$BASE_PATH"/tests/test_routes.py
touch "$BASE_PATH"/tests/test_github_api.py
touch "$BASE_PATH"/main.py

# Create HTML templates
echo "Creating HTML templates..."
touch "$BASE_PATH"/app/templates/base.html
touch "$BASE_PATH"/app/templates/index.html
touch "$BASE_PATH"/app/templates/projects.html
touch "$BASE_PATH"/app/templates/about.html

# Create config files
echo "Creating configuration files..."
touch "$BASE_PATH"/pyproject.toml
touch "$BASE_PATH"/.gitignore
touch "$BASE_PATH"/README.md
touch "$BASE_PATH"/.env

echo "Project structure created successfully at $BASE_PATH"
echo ""
echo "Next steps:"
echo "1. Run: cd $BASE_PATH"
echo "2. Initialize project with: uv init . --python 3.12"
echo "3. Install dependencies: uv add flask pytest python-dotenv requests pytest-mock"
echo "4. Update the .env file with your GitHub credentials"
echo "5. Fill in the code files with the implementation"
