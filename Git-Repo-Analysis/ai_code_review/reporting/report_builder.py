import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ReportBuilder:
    """
    Merges analysis data into a structured final report.
    """

    def build_project_summary(self, scan_metadata: Dict[str, Any], score_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the project summary section.
        """
        return {
            "total_files": scan_metadata.get("total_files", 0),
            "total_directories": scan_metadata.get("total_directories", 0),
            "total_code_files": scan_metadata.get("code_files_count", 0),
            "total_issues": score_data.get("total_issues", 0),
            "overall_score": score_data.get("overall_score", 0),
            "issue_breakdown": score_data.get("issue_breakdown", {})
        }

    def build_file_section(self, analysis_results: List[Dict[str, Any]], ai_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Build the detailed file section, merging static analysis and AI suggestions.
        """
        file_map = {res["file"]: res for res in analysis_results}
        
        # Merge AI suggestions
        for ai_res in ai_results:
            fpath = ai_res["file"]
            if fpath in file_map:
                file_map[fpath]["ai_suggestions"] = ai_res.get("ai_suggestions", "")
            else:
                pass
        
        files_output = []
        for file_path, data in file_map.items():
            issues = data.get("issues", [])
            files_output.append({
                "file": file_path,
                "issue_count": len(issues),
                "issues": issues,
                "ai_suggestions": data.get("ai_suggestions", None) 
            })
            
        return files_output

    def build_final_report(self, analysis_results: List[Dict[str, Any]], ai_results: List[Dict[str, Any]], 
                           scan_metadata: Dict[str, Any], score_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construct the full structured report.
        """
        summary = self.build_project_summary(scan_metadata, score_data)
        files_section = self.build_file_section(analysis_results, ai_results)
        
        # Extract AI insights
        ai_insights = [
            {"file": res["file"], "suggestion": res.get("ai_suggestions", "")}
            for res in ai_results if res.get("ai_suggestions")
        ]

        return {
            "project_summary": summary,
            "files": files_section,
            "ai_insights": ai_insights,
            "scores": score_data
        }
