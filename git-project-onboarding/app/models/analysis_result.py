"""
Analysis Result Model

This module defines the database schema for storing detailed analysis results
linked to a Project.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from datetime import datetime
from app.db.base import Base

class AnalysisResult(Base):
    """
    SQLAlchemy model representing the results of a code analysis run.
    
    Attributes:
        id (int): Primary key.
        project_id (int): Foreign key to the associated Project.
        file_structure (str): Text representation of the file tree.
        python_files (list): JSON list of Python file paths found.
        analysis_data (list): JSON list of detailed analysis findings.
        created_at (datetime): Timestamp of analysis.
    """
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    file_structure = Column(Text)
    python_files = Column(JSON)
    analysis_data = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
