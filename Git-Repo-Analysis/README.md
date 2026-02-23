# 🤖 AI Code Reviewer

An intelligent code analysis tool that combines static analysis with Generative AI to provide comprehensive reviews of Git repositories. This tool evaluates code quality, security, and performance, providing actionable insights and an overall project score.

## ✨ Features

- **Multi-Language Support**: Analyzes Python, JavaScript, Java, C++, TypeScript, and more.
- **Static Analysis Engine**:
  - **Quality Checks**: Detects large functions, complex logic, and style issues.
  - **Security Scanning**: Identifies risky pattern like `eval()`, hardcoded credentials, and unsafe subprocess calls.
  - **Performance Review**: Highlights potential bottlenecks and inefficient code patterns.
- **AI-Powered Insights**: Uses Google's Gemini models (e.g., Gemini 2.0 Flash) to provide deep, context-aware code reviews and improvement suggestions.
- **Scoring System**: Generates a letter grade (A-F) and a numerical score (0-100) for the repository.
- **Dual Interfaces**:
  - **Web Dashboard**: Interactive Streamlit app for easy visualization.
  - **REST API**: FastAPI backend for integration into other pipelines.

## 📂 Project Structure

```text
├── ai_code_review/         # Core Logic
│   ├── ai_engine/          # Gemini AI integration
│   ├── analyzers/          # Static analysis modules (Quality, Security, Performance)
│   ├── api/                # FastAPI application
│   ├── core/               # Git cloning and project loading
│   ├── reporting/          # Scoring and report generation
│   ├── scanner/            # File system scanning
│   └── main.py             # CLI entry point
├── cloned_repos/           # Temporary storage for analyzed repos
├── reports/                # Output directory for JSON reports
├── Config.py               # Central configuration settings
├── streamlit_app.py        # Streamlit Web UI
└── requirements.txt        # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- Git installed on your system
- A Google Gemini API Key
- (Optional) A GitHub Personal Access Token for higher rate limits

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/git-repo-analysis.git
cd git-repo-analysis
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory:

```env
# Required for AI features
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: For accessing private repos or higher API limits
GITHUB_TOKEN=your_github_token_here
```

---

## 🖥️ Usage

### Option 1: Streamlit Web Interface (Recommended)

The easiest way to use the tool is via the interactive web dashboard.

1. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Open your browser:**
   The app usually starts at `http://localhost:8501`.

3. **Analyze a Repo:**
   - Enter a GitHub URL (e.g., `https://github.com/fastapi/fastapi`).
   - (Optional) Enter your GitHub Token if the repo is private.
   - Click **"🚀 Analyze Repository"**.

### Option 2: REST API

You can run the backend as a standard API service using FastAPI.

1. **Start the API Server:**
   ```bash
   uvicorn ai_code_review.api.main:app --reload
   ```

2. **Access Documentation:**
   Open `http://127.0.0.1:8000/docs` to see the Swagger UI.

3. **Make a Request:**
   ```bash
   curl -X POST "http://127.0.0.1:8000/analyze" \
        -H "Content-Type: application/json" \
        -d '{"repo_url": "https://github.com/user/repo"}'
   ```

### Option 3: Command Line Interface (CLI)

For quick local checks without a UI:

```bash
python ai_code_review/main.py
```
Follow the prompts to enter the repository URL.

## 📊 How Scoring Works

The system starts with a perfect score (100) and applies penalties based on detected issues:

- **Quality Issues**: -1 to -5 points (Complexity, style)
- **Performance Issues**: -2 to -4 points (Loops, resource usage)
- **Security Vulnerabilities**: -2 to -10 points (Hardcoded secrets, unsafe calls)

**Grading Scale:**
- **A**: 90 - 100
- **B**: 80 - 89
- **C**: 70 - 79
- **D**: 60 - 69
- **F**: Below 60


