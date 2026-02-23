import logging
import asyncio
import os
from services.path_manager import setup_paths
from typing import List, Dict, Any

# Ensure paths
setup_paths()

try:
    from ai_code_review.analyzers.security_analyzer import SecurityAnalyzer
except ImportError:
    SecurityAnalyzer = None

try:
    from ai_code_review.ai_engine.ai_reviewer import AIReviewer
except ImportError:
    AIReviewer = None

try:
    from run_analysis import analyze_file as nexatest_analyze
    NEXATEST_AVAILABLE = True
except ImportError:
    NEXATEST_AVAILABLE = False
    def nexatest_analyze(path): return {}

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Orchestrates code analysis using NexaTest and SecurityAnalyzer.
    """
    
    def __init__(self):
        self.security_analyzer = SecurityAnalyzer() if SecurityAnalyzer else None
        self.ai_reviewer = AIReviewer() if AIReviewer else None
        
    def analyze_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Runs comprehensive analysis on a list of file paths.
        
        Args:
            file_paths (List[str]): Paths to python files.
            
        Returns:
            List[Dict]: Analysis results per file.
        """
        results = []
        logger.info(f"Analyzing {len(file_paths)} files...")

        for file_path in file_paths:
            try:
                file_report = self._analyze_single_file(file_path)
                results.append(file_report)
            except Exception as e:
                logger.error(f"Analysis failed for {file_path}: {e}")
        
        # Run AI Review for top problem files if available
        if self.ai_reviewer:
            try:
                # Pass empty string for readme_content as requested
                ai_reviews = self.ai_reviewer.generate_ai_review(results, "")
                
                # Merge AI suggestions into results
                review_map = {item['file']: item['ai_suggestions'] for item in ai_reviews}
                for res in results:
                    if res.get('file') in review_map:
                        res['ai_suggestions'] = review_map[res['file']]
                        
            except Exception as e:
                logger.error(f"AI Review failed: {e}")
                
        return results

    def _analyze_single_file(self, file_path: str) -> Dict[str, Any]:
        """Internal helper to analyze one file."""
        report = {}
        findings = []

        # 1. Run NexaTest Analysis
        if NEXATEST_AVAILABLE:
            report = nexatest_analyze(file_path)
            findings = report.get("issues", [])
        else:
            report = {"file": file_path, "summary": {}, "issues": []}

        # 2. Run Security Analysis
        if self.security_analyzer:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                security_issues = self.security_analyzer.analyze(file_path, content)
                if security_issues:
                    findings.extend(security_issues)
            except Exception as e:
                logger.error(f"Security scan failed for {file_path}: {e}")

        # 3. Update Summary
        report["issues"] = findings
        report["summary"] = {
            "total": len(findings),
            "errors": sum(1 for issue in findings if issue.get("severity") == "error"),
            "warnings": sum(1 for issue in findings if issue.get("severity") == "warning"),
            "security": sum(1 for issue in findings if issue.get("type") == "security")
        }
        
        return report
