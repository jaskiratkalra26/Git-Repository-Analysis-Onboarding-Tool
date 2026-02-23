# Git Repository Analysis & Onboarding Tool

A comprehensive tool designed to verify, onboard, and analyze GitHub repositories.

This automation suite orchestrates multiple services to clone repositories, generate folder tree structures, enforce code quality rules (NexaTest), perform security scanning, and use AI for advanced code reviews and README generation.


## Features

### GitHub Integration
- Secure authentication with GitHub
- Fetch user repositories automatically

### Repository Onboarding
- Automated repository cloning
- Generates file and folder tree structures
- Parses and verifies existing README files

### Advanced Code Analysis

NexaTest Engine checks for:
- Cyclomatic complexity
- Function length
- Naming conventions
- Docstring coverage

Security Scanning detects:
- Hardcoded credentials
- Potential security vulnerabilities

### AI-Powered Review

Integrates with:
- Google Gemini
- Ollama (Local LLM)

Features:
- Intelligent code summaries
- README generation
- Code improvement suggestions


## Installation

### Prerequisites

- Python 3.10+
- Git installed and available in system PATH
- Ollama (optional for local AI models)


## Setup Instructions

### 1. Clone the Project

git clone <your-repository-url>
cd GIT-repo-analyzer-extension


### 2. Create Virtual Environment

Windows:

python -m venv venv
venv\Scripts\activate

Mac/Linux:

python3 -m venv venv
source venv/bin/activate


### 3. Install Dependencies

pip install -r requirements.txt


## Configuration

Create a `.env` file in the root directory:

DATABASE_URL=sqlite:///./sql_app.db

GITHUB_API_URL=https://api.github.com

GOOGLE_API_KEY=your_gemini_api_key_here

OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3


## Usage

### Run Full Pipeline

python main.py

This will:

1. Fetch repositories
2. Clone repositories
3. Generate folder trees
4. Run NexaTest checks
5. Run security scans
6. Generate AI reviews
7. Store results in database


### Run Individual Modules

Verify Database:

python verify_db_storage.py

Run Pipeline Tests:

python test_pipeline.py


Project Structure

GIT-repo-analyzer-extension/

├── main.py                          # Application entry point
├── services/                        # Core services
│   ├── orchestrator_service.py      # Pipeline coordinator
│   ├── github_service.py            # GitHub API integration
│   ├── analysis_service.py          # Code analysis management
│   ├── ai_service.py                # AI integration
│   └── ...
├── cloned_repos/                    # Cloned repositories (ignored by Git)
├── git-project-onboarding/          # Repo onboarding and database models
├── Git-Repo-Analysis/               # AI analysis and security scanning
├── NexaTest/                        # Code quality engine
├── Nexatest--FolderTreeStructure/   # Folder tree generator
└── sql_app.db                       # SQLite database


## Modules Overview

### Orchestrator Service

The main controller that connects GitHub service, database storage, analysis modules, and AI modules into one automated pipeline.


### NexaTest

A rule-based engine for enforcing coding standards.

Rules include:

- Complexity Rule → Detects complex functions
- Naming Rule → Enforces PEP8 naming
- Docstring Rule → Detects missing documentation


### AI Code Review

Uses AI models to:

- Analyze code
- Suggest improvements
- Generate documentation
- Detect logical issues

Supports:

- Google Gemini
- Ollama


## Database

All results are stored in:

sql_app.db

Stores:

- User information
- Repository metadata
- Analysis results
- AI reviews


## Summary

This tool provides a complete automated GitHub repository onboarding and analysis pipeline combining static code analysis, security scanning, AI-based review, repository structure generation, and database storage.



