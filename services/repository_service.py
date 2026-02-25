import logging
import asyncio
from services.path_manager import setup_paths

# Setup paths before imports
setup_paths()

try:
    from app.db.database import SessionLocal, engine
    from app.models.repository import Repository
    from app.models.user import User
    from app.models.project import Project
    from app.models.analysis_result import AnalysisResult
    from app.db.base import Base
except ImportError:
    logging.error("Failed to import Database models from git-project-onboarding.")
    # Define stubs
    SessionLocal = None
    engine = None
    Repository = None
    User = None
    Project = None
    AnalysisResult = None
    Base = None

logger = logging.getLogger(__name__)

class RepositoryService:
    """
    Manages database interactions for User, Repository, and Project entities.
    Handles data persistence and retrieval.
    """
    def __init__(self):
        self.log = logging.getLogger(__name__)
        # Ensure tables exist
        try:
            if Base and engine:
                Base.metadata.create_all(bind=engine)
        except Exception as e:
            self.log.error(f"Failed to create tables: {e}")

    def get_db(self):
        """Yields a database session."""
        if not SessionLocal:
            raise RuntimeError("Database session factory is not configured.")
        db = SessionLocal()
        try:
            return db
        except Exception:
            db.close()
            raise

    async def get_or_create_user(self, user_data: dict, token: str):
        """Finds or creates a User in the database."""
        db = self.get_db()
        try:
            user = db.query(User).filter(User.github_id == user_data['id']).first()
            if not user:
                self.log.info(f"Creating new user: {user_data.get('login')}")
                user = User(
                    github_id=user_data['id'],
                    github_username=user_data['login'],
                    github_email=user_data.get('email'),
                    github_access_token=token
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            return user
        finally:
            db.close()

    async def get_or_create_repository(self, repo_data: dict, user_id: int):
        """Finds or creates a Repository in the database linked to a User."""
        db = self.get_db()
        try:
            repo = db.query(Repository).filter(Repository.github_repo_id == repo_data['id']).first()
            if not repo:
                self.log.info(f"Connecting repository: {repo_data.get('full_name')}")
                repo = Repository(
                    github_repo_id=repo_data['id'],
                    name=repo_data['name'],
                    full_name=repo_data['full_name'],
                    repo_url=repo_data['html_url'],
                    is_private=repo_data['private'],
                    default_branch=repo_data.get('default_branch', 'main'),
                    owner_name=repo_data['owner']['login'],
                    connected_by_user_id=user_id
                )
                db.add(repo)
                db.commit()
                db.refresh(repo)
            return repo
        finally:
            db.close()

    async def get_project_by_repo_id(self, repo_id: int):
        """Retrieve existing project for a repository ID."""
        db = self.get_db()
        try:
            project = db.query(Project).filter(Project.repository_id == repo_id).first()
            if project:
                return {
                    "id": project.id,
                    "project_name": project.project_name,
                    "description": project.description,
                    "features": project.features,
                    # Note: Existing implementation doesn't store this, potentially
                    # handled by analysis logic or regenerated. Keeping it consistent.
                }
            return None
        finally:
            db.close()

    async def update_project(self, repo_id: int, project_data: dict):
        """Updates an existing project with new metadata."""
        db = self.get_db()
        try:
            project = db.query(Project).filter(Project.repository_id == repo_id).first()
            if project:
                if project_data.get("project_name"):
                    project.project_name = project_data["project_name"]
                if project_data.get("description"):
                    project.description = project_data["description"]
                if project_data.get("features") is not None:
                    project.features = project_data["features"]
                db.commit()
                db.refresh(project)
                return project
            return None
        finally:
            db.close()

    async def create_project(self, project_data: dict, repo_id: int, user_id: int):
        """Creates a new Project record."""
        db = self.get_db()
        try:
            new_project = Project(
                project_name=project_data.get("project_name", "Untitled"),
                description=project_data.get("description", ""),
                features=project_data.get("features", []),
                repository_id=repo_id,
                created_by=user_id
            )
            db.add(new_project)
            db.commit()
            db.refresh(new_project)
            return new_project
        except Exception as e:
            db.rollback()
            self.log.error(f"Failed to create project: {e}")
            return None
        finally:
            db.close()

    async def create_analysis_result(self, project_id: int, file_structure: str, python_files: list, analysis_data: list):
        """Creates a new AnalysisResult record linked to a Project."""
        db = self.get_db()
        try:
            new_result = AnalysisResult(
                project_id=project_id,
                file_structure=file_structure,
                python_files=python_files,
                analysis_data=analysis_data
            )
            db.add(new_result)
            db.commit()
            db.refresh(new_result)
            return new_result
        except Exception as e:
            db.rollback()
            self.log.error(f"Failed to create analysis result: {e}")
            return None
        finally:
            db.close()
            
    async def get_latest_analysis_result(self, project_id: int):
        """Retrieves the most recent analysis result for a project."""
        db = self.get_db()
        try:
            return db.query(AnalysisResult).filter(
                AnalysisResult.project_id == project_id
            ).order_by(AnalysisResult.created_at.desc()).first()
        finally:
            db.close()

