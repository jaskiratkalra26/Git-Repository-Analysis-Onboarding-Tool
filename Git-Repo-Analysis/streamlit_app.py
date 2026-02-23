import streamlit as st
import os
import sys
import logging
import asyncio
from typing import Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Logging to display in Streamlit
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Add module paths
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'ai_code_review')))

# Import Application Modules
# Note: Adjusting imports based on project structure
try:
    from Config import Config
    from ai_code_review.settings import get_github_token, DEFAULT_CLONE_DIR
    from ai_code_review.core.repo_manager import RepoManager
    from ai_code_review.core.project_loader import ProjectLoader
    from ai_code_review.scanner.directory_scanner import DirectoryScanner
    from ai_code_review.scanner.file_collector import FileCollector
    from ai_code_review.analyzers.analysis_engine import AnalysisEngine
    from ai_code_review.ai_engine.ai_reviewer import AIReviewer
    from ai_code_review.reporting.score_engine import ScoreEngine
    from ai_code_review.reporting.report_builder import ReportBuilder
    from ai_code_review.reporting.export_manager import ExportManager
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🤖",
    layout="wide"
)

def main():
    st.title("🤖 AI Code Reviewer")
    st.markdown("Analyze your Git repositories with AI-powered insights.")

    # Sidebar Configuration
    st.sidebar.header("Configuration")
    
    # 1. Input: Repository URL
    default_repo = "https://github.com/fastapi/fastapi"
    repo_url = st.sidebar.text_input("GitHub Repository URL", value="", placeholder=default_repo)
    
    # 2. Input: GitHub Token (Optional)
    env_token = get_github_token()
    token_input = st.sidebar.text_input("GitHub Token (Optional)", value=env_token if env_token else "", type="password", help="Providing a token increases API limits and allows access to private repos.")
    
    # Analysis Trigger
    if st.sidebar.button("🚀 Analyze Repository"):
        if not repo_url:
            st.error("Please provide a valid GitHub Repository URL.")
        else:
            st.session_state['analyzing'] = True
            st.session_state['repo_url'] = repo_url
            st.session_state['token'] = token_input
            
    if st.session_state.get('analyzing'):
        run_analysis(st.session_state['repo_url'], st.session_state['token'])

def run_analysis(repo_url: str, token: Optional[str]):
    # Prevent git from asking for credentials in terminal which hangs the app
    os.environ['GIT_TERMINAL_PROMPT'] = '0'
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    try:
        # 1. Clone Repository
        status_text.text(f"🔄 Cloning repository: {repo_url}...")
        repo_manager = RepoManager(DEFAULT_CLONE_DIR)
        try:
            project_path = repo_manager.clone_repository(repo_url, token)
            progress_bar.progress(10)
            st.success(f"✅ Repository cloned to: {project_path}")
        except Exception as e:
            st.session_state['analyzing'] = False
            if "Authentication required" in str(e):
                st.error("🔒 Repository is private or requires authentication. Please provide a valid GitHub Token.")
            else:
                st.error(f"❌ Failed to clone repository: {e}")
            return

        # 2. Load and Validate
        status_text.text("📂 Validating project structure...")
        loader = ProjectLoader(project_path)
        if not loader.validate_project():
            st.session_state['analyzing'] = False
            st.error("❌ Invalid project structure or empty directory.")
            return
        progress_bar.progress(20)
        
        # 3. Directory Scan
        status_text.text("🔍 Scanning directories...")
        scanner = DirectoryScanner(project_path)
        scan_results = scanner.scan()
        progress_bar.progress(30)
        
        col1, col2 = st.columns(2)
        col1.metric("Files Found", scan_results.get("total_files", 0))
        col2.metric("Directories Found", scan_results.get("total_directories", 0))

        # 4. Collect Files
        status_text.text("📝 Collecting code files...")
        file_collector = FileCollector(scan_results["all_files"])
        code_files = file_collector.get_code_files()
        
        if not code_files:
            st.session_state['analyzing'] = False
            st.warning("⚠️ No supported code files found.")
            return
        
        st.info(f"Found {len(code_files)} supported code files for analysis.")
        progress_bar.progress(40)

        # 5. Static Analysis
        status_text.text("⚙️ Running static analysis...")
        analysis_engine = AnalysisEngine()
        
        analysis_results = []
        
        if hasattr(analysis_engine, 'analyze_project'):
            analysis_results = analysis_engine.analyze_project(code_files)
        else:
            total_files = len(code_files)
            for i, file_path in enumerate(code_files):
                status_text.text(f"Running static analysis... ({i+1}/{total_files})")
                try:
                    result = analysis_engine.analyze_file(file_path)
                    analysis_results.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing file {file_path}: {e}")
        
        progress_bar.progress(70)
        
        # 6. AI Review
        api_key = os.getenv(Config.ENV_GEMINI_API_KEY)
        if not api_key:
            st.warning("⚠️ GEMINI_API_KEY not found. AI Review will be skipped/limited.")
            
        status_text.text("🧠 Running AI Review (this may take a moment)...")
        ai_reviewer = AIReviewer()
        
        # Read README
        readme_content = ""
        readme_path = os.path.join(project_path, "README.md")
        if not os.path.exists(readme_path):
             readme_path = os.path.join(project_path, "readme.md")
        
        if os.path.exists(readme_path):
            try:
                with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                    readme_content = f.read()
            except Exception:
                pass
        
        try:
            ai_results = ai_reviewer.generate_ai_review(analysis_results, readme_content)
        except Exception as e:
            st.error(f"AI Review failed: {e}")
            ai_results = []
            
        progress_bar.progress(90)

        # 7. Scoring
        status_text.text("📊 Calculating scores...")
        score_engine = ScoreEngine()
        score_data = score_engine.calculate_project_score(analysis_results)

        # 8. Report Building
        report_builder = ReportBuilder()
        final_report = report_builder.build_final_report(
            analysis_results=analysis_results,
            ai_results=ai_results,
            scan_metadata={
                "total_files": scan_results.get("total_files", 0),
                "total_directories": scan_results.get("total_directories", 0),
                "code_files_count": len(code_files)
            },
            score_data=score_data
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis Complete!")
        
        # Clear analyzing state so we don't re-run on interaction, but keep results
        st.session_state['analyzing'] = False
        display_results(final_report, score_data)

    except Exception as e:
        st.session_state['analyzing'] = False
        st.error(f"❌ An error occurred: {str(e)}")
        logger.exception("Analysis failed")

def display_results(final_report, score_data):
    st.divider()
    st.header("🏁 Analysis Results")

    # Score Summary
    st.subheader("Project Score")
    
    # Map ScoreEngine output keys to UI
    total_score = score_data.get("overall_score", 0)
    
    # Calculate Grade
    if total_score >= 90:
        grade = "A"
    elif total_score >= 80:
        grade = "B"
    elif total_score >= 70:
        grade = "C"
    elif total_score >= 60:
        grade = "D"
    else:
        grade = "F"
    
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Score", value=f"{total_score}/100")
    col2.metric(label="Grade", value=grade)
    col3.metric(label="Total Issues", value=score_data.get("total_issues", 0))
    
    # Detailed Scores
    with st.expander("Detailed Scoring"):
        st.json(score_data)

    # AI Review Section
    st.subheader("🧠 AI Code Reviews")
    ai_insights = final_report.get("ai_insights", [])
    
    if ai_insights:
        for insight in ai_insights:
            file_path = insight.get("file", "Unknown")
            file_name = Path(file_path).name
            
            with st.expander(f"Review: {file_name}", expanded=True):
                st.markdown(insight.get("suggestion", "No details available."))
    else:
        st.info("No AI reviews generated (either no issues found or AI analysis skipped).")
    
    # Issues List
    st.subheader("🚨 Detected Issues")
    
    # Helper to clean up file paths for display
    def clean_path(p):
        return Path(p).name

    files_data = final_report.get("files", [])
    has_issues = False
    
    if files_data:
        for file_result in files_data:
            issues = file_result.get("issues", [])
            if issues:
                has_issues = True
                file_name = clean_path(file_result.get("file", "Unknown"))
                with st.expander(f"{file_name} ({len(issues)} issues)"):
                    for issue in issues:
                        severity = issue.get("severity", "INFO").upper()
                        icon = "🔴" if severity == "HIGH" else "🟠" if "MEDIUM" in severity else "🔵"
                        st.markdown(f"**{icon} {severity}**: {issue.get('message', 'No description')}")
                        st.caption(f"Line: {issue.get('line', 'N/A')} | Type: {issue.get('type', 'Unknown')}")
    
    if not has_issues:
        st.success("No major issues detected!")

    # Full JSON Report
    if st.checkbox("Show Full JSON Report"):
        st.json(final_report)

if __name__ == "__main__":
    main()
