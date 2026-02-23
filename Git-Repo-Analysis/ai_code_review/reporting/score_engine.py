import logging
import sys
import os
from typing import List, Dict, Any

# Add root directory to path to import Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Config import Config

logger = logging.getLogger(__name__)

class ScoreEngine:
    """
    Calculates project and file scores based on static analysis issues.
    """

    def __init__(self):
        self.issue_penalties = Config.ISSUE_PENALTIES
    
    def _calculate_file_metrics(self, issues: List[Dict[str, Any]]) -> tuple[int, Dict[str, int]]:
        """
        Helper to calculate both score and issue breakdown in a single loop.
        """
        score = Config.INITIAL_FILE_SCORE
        breakdown = {"quality": 0, "security": 0, "performance": 0}
        
        for issue in issues:
            issue_type = issue.get("type", "quality").lower()
            severity = issue.get("severity", "medium").lower()
            
            # Update breakdown
            if issue_type in breakdown:
                breakdown[issue_type] += 1
            else:
                breakdown.setdefault("other", 0)
                breakdown["other"] += 1
            
            # Calculate Penalty
            penalty = 0
            if issue_type in self.issue_penalties:
                penalty = self.issue_penalties[issue_type].get(severity, 0) # Default to 0 if severity not found
            else:
                # Fallback for unknown types if any? Or standard default?
                # Keeping it 0 for unknown types safe
                pass

            score += penalty 

        return max(0, score), breakdown

    def calculate_file_score(self, issues: List[Dict[str, Any]]) -> int:
        """
        Compute score for a single file starting from 100.
        Score cannot go below 0.
        """
        score, _ = self._calculate_file_metrics(issues)
        return score

    def calculate_project_score(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall project statistics and score.
        """
        total_files = len(analysis_results)
        if total_files == 0:
            return {
                "overall_score": Config.INITIAL_FILE_SCORE,
                "average_file_score": Config.INITIAL_FILE_SCORE,
                "total_issues": 0,
                "issue_breakdown": {
                    "quality": 0,
                    "security": 0,
                    "performance": 0
                }
            }

        total_score = 0
        total_issues = 0
        project_breakdown = {
            "quality": 0,
            "security": 0,
            "performance": 0
        }

        for result in analysis_results:
            issues = result.get("issues", [])
            
            # Calculate both score and breakdown in one pass
            file_score, file_breakdown = self._calculate_file_metrics(issues)
            
            total_score += file_score
            total_issues += len(issues)
            
            # Aggregate breakdown
            for k, v in file_breakdown.items():
                if k in project_breakdown:
                    project_breakdown[k] += v
                else:
                    project_breakdown.setdefault("other", 0)
                    project_breakdown["other"] += v

        avg_score = int(total_score / total_files)
        
        return {
            "overall_score": avg_score,
            "average_file_score": avg_score,
            "total_issues": total_issues,
            "issue_breakdown": project_breakdown
        }
