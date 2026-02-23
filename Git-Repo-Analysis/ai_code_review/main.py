import os
import logging
from dotenv import load_dotenv

# Import our custom modules
from settings import get_github_token, DEFAULT_CLONE_DIR
from core.repo_manager import RepoManager
from core.project_loader import ProjectLoader
from scanner.directory_scanner import DirectoryScanner
from scanner.file_collector import FileCollector
from scanner.readme_extractor import ReadmeExtractor
from analyzers.analysis_engine import AnalysisEngine
from ai_engine.ai_reviewer import AIReviewer
from reporting.score_engine import ScoreEngine
from reporting.report_builder import ReportBuilder
from reporting.export_manager import ExportManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the AI Code Review System.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    print("=== AI Code Review System: Phase 2 ===")
    
    # 1. Ask user for repo_url
    repo_url = input("Enter GitHub Repository URL: ").strip()
    if not repo_url:
        logger.error("Error: Repository URL cannot be empty.")
        return

    # 2. Try to read GitHub token
    token = get_github_token()
    if token:
        logger.info("GitHub token found in environment.")
    else:
        logger.info("No GITHUB_TOKEN found. Proceeding with public access.")

    # 3. Initialize RepoManager
    try:
        repo_manager = RepoManager(DEFAULT_CLONE_DIR)
        
        # 4. Clone Repo
        logger.info("Starting cloning process...")
        project_path = repo_manager.clone_repository(repo_url, token)
        
        print(f"\nRepository cloned successfully.\nPath: {project_path}\n")

        # 5. Initialize ProjectLoader
        project_loader = ProjectLoader(project_path)

        # 6. Validate Project
        if project_loader.validate_project():
            print("Project validated successfuly.")

            # --- Phase 2: Project Scanning ---
            print("\nStarting Phase-2: Project Scanning...")

            # 7. Directory Scanner
            scanner = DirectoryScanner(project_path)
            scan_result = scanner.scan()

            # 8. File Collector
            collector = FileCollector(scan_result["all_files"])
            code_files = collector.get_code_files()
            file_type_counts = collector.categorize_files()

            # 9. Readme Extractor
            readme_extractor = ReadmeExtractor(project_path)
            readme_path = readme_extractor.find_readme()
            # We don't necessarily need to print the content, but we extract it as requested.
            readme_content = readme_extractor.extract_content()

            # Summary Output
            print("\n## Project Scan Summary:\n")
            print(f"Total files: {scan_result['total_files']}")
            print(f"Total directories: {scan_result['total_directories']}")
            print(f"Code files detected: {len(code_files)}")

            print("\nFile type distribution:")
            if file_type_counts:
                for ext, count in file_type_counts.items():
                    print(f"{ext}: {count}")
            else:
                print("No supported code files found.")

            print(f"\nREADME found: {'Yes' if readme_path else 'No'}")

            # --- Phase 3: Static Analysis ---
            print("\nStarting Phase-3: Rule-based Static Analysis...")

            engine = AnalysisEngine()
            analysis_results = engine.analyze_project(code_files)

            # Summary stats
            total_issues = 0
            file_issue_counts = []

            for res in analysis_results:
                count = len(res["issues"])
                total_issues += count
                if count > 0:
                    try:
                        rel_path = os.path.relpath(res["file"], project_path)
                    except ValueError:
                        rel_path = res["file"]
                    file_issue_counts.append((rel_path, count))

            # Sort by issue count descending
            file_issue_counts.sort(key=lambda x: x[1], reverse=True)

            print("\n## Analysis Complete\n")
            print(f"Files analyzed: {len(code_files)}")
            print(f"Total issues found: {total_issues}")

            if file_issue_counts:
                print("\nTop files with most issues:")
                for fpath, count in file_issue_counts[:5]:
                    print(f"- {fpath} ({count} issues)")

            # --- Phase 4: AI Review ---
            ai_recommendations = []
            if os.getenv("GEMINI_API_KEY"):
                print("\nStarting Phase-4: AI-Powered Code Review...")
                
                ai_reviewer = AIReviewer()
                ai_recommendations = ai_reviewer.generate_ai_review(analysis_results, readme_content)

                print(f"\nAI Review Completed using Gemini 2.5 Flash")
                print(f"Files reviewed by AI: {len(ai_recommendations)}")
                
                if ai_recommendations:
                    print("\nAI Recommendations generated for:")
                    for item in ai_recommendations:
                        try:
                            rel_path = os.path.relpath(item["file"], project_path)
                        except ValueError:
                            rel_path = item["file"]
                        print(f"- {rel_path}")
            else:
                print("\nSkipping Phase-4: GEMINI_API_KEY not found. Analysis limited to rule-based tests.")

            # --- Phase 5: Reporting ---
            print("\nStarting Phase-5: Generating Final Report...")
            
            # 1. Initialize ScoreEngine & Calculate Scores
            score_engine = ScoreEngine()
            score_data = score_engine.calculate_project_score(analysis_results)
            
            # 2. Prepare Metadata
            scan_metadata = {
                "total_files": scan_result['total_files'],
                "total_directories": scan_result['total_directories'],
                "code_files_count": len(code_files) 
            }
            
            # 3. Initialize ReportBuilder & Generate Report
            report_builder = ReportBuilder()
            final_report = report_builder.build_final_report(
                analysis_results, 
                ai_recommendations, 
                scan_metadata, 
                score_data
            )
            
            # 4. Initialize ExportManager & Save Report
            export_manager = ExportManager()
            reports_dir = os.path.abspath("reports")
            
            export_manager.export_to_json(final_report, os.path.join(reports_dir, "project_report.json"))
            export_manager.export_to_txt(final_report, os.path.join(reports_dir, "project_report.txt"))
            
            print("\nFinal Report Generated Successfully")
            print(f"Location: {os.path.join(reports_dir, 'project_report.txt')}")

        else:
            logger.error("Project validation failed. The cloned directory might be empty or invalid.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
