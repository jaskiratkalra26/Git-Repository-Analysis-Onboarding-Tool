import logging
import asyncio
from services.github_service import GitHubService
from services.repository_service import RepositoryService
from services.clone_service import CloneService
from services.scanning_service import ScanningService
from services.analysis_service import AnalysisService
from services.ai_service import AIService

logger = logging.getLogger(__name__)

class OrchestratorService:
    """
    Coordinates the entire workflow: GitHub -> DB -> Clone -> Scan -> Analyze -> AI -> Report.
    """
    def __init__(self):
        self.github_service = GitHubService()
        self.repository_service = RepositoryService()
        self.clone_service = CloneService()
        self.scanning_service = ScanningService()
        self.analysis_service = AnalysisService()
        self.ai_service = AIService()

    async def authenticate_and_get_repos(self, token: str):
        """
        Public method to authenticate and fetch repositories.
        Delegates to GitHubService.
        """
        user = await self.github_service.authenticate_user(token)
        if not user:
            return None
        return await self.github_service.get_repositories(token)

    def get_repository_file_structure(self, repo_path: str, limit_depth: int = -1) -> str:
        """
        Returns the visual file structure of a repository.
        
        Args:
            repo_path (str): The local path to the repository.
            limit_depth (int): Maximum depth to traverse. -1 for unlimited.
            
        Returns:
            str: The tree structure string.
        """
        return self.scanning_service.get_repository_structure(repo_path, limit_depth)

    async def generate_project_report(self, token: str, github_repo_id: int):
        """
        Main entry point to generate a full report for a repository.
        """
        logger.info(f"Starting report generation for Repo ID: {github_repo_id}")
        
        try:
            # 1. Fetch Repository Details from GitHub
            repo_details = await self.github_service.get_repo_details(token, github_repo_id)
            if not repo_details:
                raise ValueError("Could not fetch repository details from GitHub.")

            # 2. Get User Info for linkage
            user_data = await self.github_service.authenticate_user(token)
            if not user_data:
                raise ValueError("Authentication failed.")
            
            # 3. DB: Ensure User & Repository exist
            user = await self.repository_service.get_or_create_user(user_data, token)
            repo = await self.repository_service.get_or_create_repository(repo_details, user.id)

            # 4. Check if Project Analysis already exists in DB
            # Note: We might want to force refresh, but per original logic we check first
            existing_project = await self.repository_service.get_project_by_repo_id(repo.id)
            
            # 5. Clone Repository (Blocking -> Thread)
            repo_url = repo.repo_url
            repo_name = repo.name
            
            # Run cloning in a thread to keep async loop responsive
            repo_path = await asyncio.to_thread(
                self.clone_service.ensure_cloned, repo_url, token
            )
            
            if not repo_path:
                logger.error("Cloning failed. Analysis will be incomplete.")

            # 6. Scan for Files (Blocking -> Thread)
            python_files = []
            if repo_path:
                python_files = await asyncio.to_thread(
                    self.scanning_service.scan_for_python_files, repo_path
                )

            # 7. Run Logic - Either fetch existing or generate new
            
            project_metadata = {}
            needs_ai_analysis = True

            if existing_project:
                # Check if it has meaningful content
                desc = existing_project.get("description")
                feats = existing_project.get("features")
                if desc or (feats and len(feats) > 0):
                    logger.info(f"Using existing project metadata for {repo_name}")
                    project_metadata = existing_project
                    needs_ai_analysis = False
                else:
                    logger.info(f"Existing project metadata found but empty for {repo_name}. Regenerating AI analysis...")

            if needs_ai_analysis:
                # 8. AI Analysis (README Parsing)
                logger.info(f"Generating new AI analysis for {repo_name}...")
                readme_content = await self.github_service.get_readme(token, repo.full_name)
                extracted_data = await self.ai_service.parse_readme(readme_content)
                
                # 9. Save new Project to DB
                # Merge extracted data with defaults
                project_data = {
                    "project_name": extracted_data.get("project_name") or repo.name,
                    "description": extracted_data.get("description", ""),
                    "features": extracted_data.get("features", [])
                }
                
                if existing_project:
                    # Update existing record
                    new_project = await self.repository_service.update_project(repo.id, project_data)
                    # If update fails or returns None, we still use the data locally
                    if not new_project:
                         logger.warning("Failed to update project in DB, using local data.")
                         # Construct a dict-like object or use dict directly
                         project_metadata = project_data
                    else:
                        project_metadata = {
                            "project_name": new_project.project_name,
                            "description": new_project.description,
                            "features": new_project.features
                        }
                else:
                    # Create new record
                    new_project = await self.repository_service.create_project(project_data, repo.id, user.id)
                    project_metadata = {
                        "project_name": new_project.project_name,
                        "description": new_project.description,
                        "features": new_project.features
                    }

            # 10. Run Code Analysis (Blocking -> Thread)
            # We run this always to get fresh results on the checked-out code
            analysis_results = []
            if python_files:
                analysis_results = await asyncio.to_thread(
                    self.analysis_service.analyze_files, python_files
                )

            # 11. Construct Final Response
            # Get Repository Tree Structure
            file_structure = ""
            if repo_path:
                file_structure = self.scanning_service.get_repository_structure(repo_path, limit_depth=3)

            return {
                "project_name": project_metadata.get("project_name"),
                "description": project_metadata.get("description"),
                "features": project_metadata.get("features"),
                "file_structure": file_structure,
                "python_files": python_files,
                "analysis_results": analysis_results
            }

        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return None
