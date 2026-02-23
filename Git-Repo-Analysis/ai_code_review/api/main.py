import os
import sys
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix sys.path to allow imports from parent packages
# Add ai_code_review directory
sys.path.append(str(Path(__file__).resolve().parent.parent))
# Add project root (for Config.py)
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Import custom modules
from settings import get_github_token, DEFAULT_CLONE_DIR
from core.repo_manager import RepoManager
from core.project_loader import ProjectLoader
from scanner.directory_scanner import DirectoryScanner
from scanner.file_collector import FileCollector
from analyzers.analysis_engine import AnalysisEngine
from ai_engine.ai_reviewer import AIReviewer
from reporting.score_engine import ScoreEngine
from reporting.report_builder import ReportBuilder
from reporting.export_manager import ExportManager
from Config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Code Reviewer API", version="1.0")

class AnalyzeRequest(BaseModel):
    repo_url: str
    github_token: Optional[str] = None

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Code Reviewer API is running"}

@app.post("/analyze")
def analyze_repo(request: AnalyzeRequest):
    """
    Analyze a GitHub repository.
    Steps:
    1. Clone Repo
    2. Scan & Collect Files
    3. Run Static Analysis
    4. Run AI Review (Gemini)
    5. Calculate Scores
    6. Generate Report
    """
    repo_url = request.repo_url
    token = request.github_token or get_github_token()
    
    try:
        # 1. Clone Repository
        logger.info(f"Cloning repository: {repo_url}")
        repo_manager = RepoManager(DEFAULT_CLONE_DIR)
        try:
            project_path = repo_manager.clone_repository(repo_url, token)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to clone repository: {str(e)}")
        
        # 2. Load Project & Validate
        logger.info(f"Loading project from: {project_path}")
        loader = ProjectLoader(project_path)
        if not loader.validate_project():
             raise HTTPException(status_code=400, detail="Invalid project structure or directory is empty.")

        # 3. Directory Scan
        logger.info("Scanning directory structure...")
        scanner = DirectoryScanner(project_path)
        scan_results = scanner.scan()
        
        # 4. Collect Code Files
        logger.info("Collecting code files...")
        file_collector = FileCollector(scan_results["all_files"])
        code_files = file_collector.get_code_files()
        
        if not code_files:
            raise HTTPException(status_code=400, detail="No supported code files found in the repository.")

        # 5. Static Analysis
        logger.info(f"Running static analysis on {len(code_files)} files...")
        analysis_engine = AnalysisEngine()
        # Use analyze_project if available, otherwise manual loop
        if hasattr(analysis_engine, 'analyze_project'):
            analysis_results = analysis_engine.analyze_project(code_files)
        else:
            analysis_results = []
            for file_path in code_files:
                try:
                    result = analysis_engine.analyze_file(file_path)
                    analysis_results.append(result)
                except Exception as e:
                    logger.error(f"Error analyzing file {file_path}: {e}")

        # 6. AI Review
        logger.info("Running AI Review...")
        ai_reviewer = AIReviewer()
        
        # Read README for context
        readme_content = ""
        readme_path = os.path.join(project_path, "README.md")
        if not os.path.exists(readme_path):
             readme_path = os.path.join(project_path, "readme.md")
             
        if os.path.exists(readme_path):
             try:
                 with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                     readme_content = f.read()
             except Exception:
                 logger.warning("Could not read README.md")

        ai_results = ai_reviewer.generate_ai_review(analysis_results, readme_content)

        # 7. Scoring
        logger.info("Calculating scores...")
        score_engine = ScoreEngine()
        project_score_data = score_engine.calculate_project_score(analysis_results)
        
        # 8. Report Building
        logger.info("Building final report...")
        report_builder = ReportBuilder()
        
        final_report = report_builder.build_final_report(
            analysis_results=analysis_results,
            ai_results=ai_results,
            scan_metadata={
                "total_files": scan_results.get("total_files", 0),
                "total_directories": scan_results.get("total_directories", 0),
                "code_files_count": len(code_files)
            },
            score_data=project_score_data
        )

        # 9. Export Reports
        export_manager_inst = ExportManager()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = Path(project_path).name
        
        # JSON Export
        json_filename = f"project_report_{project_name}_{timestamp}.json"
        json_path = os.path.join("reports", json_filename)
        export_manager_inst.export_to_json(final_report, json_path)
        
        # Text Export
        txt_filename = f"project_report_{project_name}_{timestamp}.txt"
        txt_path = os.path.join("reports", txt_filename)
        export_manager_inst.export_to_txt(final_report, txt_path)
        
        return final_report

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("Analysis failed with unexpected error")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
