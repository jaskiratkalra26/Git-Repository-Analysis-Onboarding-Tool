import json
import os
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ExportManager:
    """
    Handles exporting reports to disk in various formats.
    """

    def export_to_json(self, report: Dict[str, Any], output_path: str):
        """
        Save report as JSON.
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Add timestamp
            report_data = report.copy()
            report_data["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=4)
            logger.info(f"JSON report saved to {output_path}")
        except Exception as e:
            logger.error(f"Failed to export JSON report: {e}")

    def export_to_txt(self, report: Dict[str, Any], output_path: str):
        """
        Save report as a formatted text file.
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            summary = report.get("project_summary", {})
            scores = report.get("scores", {})
            breakdown = scores.get("issue_breakdown", {})
            files = report.get("files", [])
            ai_insights = report.get("ai_insights", [])
            
            lines = []
            lines.append("# PROJECT ANALYSIS REPORT")
            lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            lines.append(f"Overall Score: {scores.get('overall_score', 0)}/100")
            lines.append(f"Total Files Scanned: {summary.get('total_files', 0)}")
            lines.append(f"Total Issues Found: {summary.get('total_issues', 0)}")
            lines.append("")
            lines.append("Issue Breakdown:")
            lines.append(f"Quality: {breakdown.get('quality', 0)}")
            lines.append(f"Security: {breakdown.get('security', 0)}")
            lines.append(f"Performance: {breakdown.get('performance', 0)}")
            lines.append("")
            lines.append("Top Problem Files:")
            
            # Sort files by issue count
            sorted_files = sorted(files, key=lambda x: x['issue_count'], reverse=True)
            top_files = sorted_files[:5]
            
            for f in top_files:
                fname = os.path.basename(f['file'])
                lines.append(f"* {fname} ({f['issue_count']} issues)")
            
            lines.append("")
            lines.append("## AI Recommendations:")
            lines.append("")
            
            if not ai_insights:
                lines.append("No AI recommendations generated.")
            else:
                for item in ai_insights:
                    fname = os.path.basename(item['file'])
                    suggestion = item.get('suggestion', '').strip()
                    lines.append(f"{fname}:\n{suggestion}")
                    lines.append("\n" + "-"*40 + "\n")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
                
            logger.info(f"Text report saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export TXT report: {e}")

    def export_detailed_txt(self, files_data: list[Dict[str, Any]], output_path: str):
        """
        Save a detailed file-wise issue report to a text file.
        Format contains specific details per file.
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            lines = []
            
            lines.append("=" * 50)
            lines.append("PROJECT FILE-WISE ISSUE REPORT")
            lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("=" * 30)
            lines.append("")
            
            for file_data in files_data:
                file_path = file_data.get("file", "Unknown")
                file_name = os.path.basename(file_path)
                file_score = file_data.get("score", "N/A")
                issues = file_data.get("issues", [])
                total_issues = len(issues)
                ai_suggestions = file_data.get("ai_suggestions")
                
                lines.append(f"File Name: {file_name}")
                lines.append(f"File Path: {file_path}")
                lines.append(f"File Score: {file_score}")
                lines.append(f"Total Issues: {total_issues}")
                lines.append("")
                
                if total_issues == 0:
                    lines.append("No issues detected")
                else:
                    lines.append("ISSUES:")
                    for issue in issues:
                        pk = issue.get('type', 'unknown')
                        sev = issue.get('severity', 'unknown')
                        msg = issue.get('message', '')
                        line = issue.get('line', 'N/A')
                        lines.append(f"* Type: {pk}")
                        lines.append(f"  Severity: {sev}")
                        lines.append(f"  Message: {msg}")
                        lines.append(f"  Line: {line}")
                        lines.append("")

                if ai_suggestions:
                    lines.append("AI SUGGESTIONS:")
                    lines.append(ai_suggestions)
                
                lines.append("\n" + "-" * 50 + "\n")
                
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
                
            logger.info(f"Detailed detailed_file_issues report saved to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save detailed file report: {e}")
