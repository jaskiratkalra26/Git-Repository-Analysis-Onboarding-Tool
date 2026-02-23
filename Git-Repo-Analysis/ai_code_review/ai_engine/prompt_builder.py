from typing import List, Dict

class PromptBuilder:
    """
    Constructs prompts for the AI model based on project context and analysis results.
    """

    def build_project_context(self, readme_content: str) -> str:
        """
        Summarizes the README content to provide project context.

        Args:
            readme_content (str): The full content of the README file.

        Returns:
            str: A short summary block (first 500-700 characters).
        """
        if not readme_content:
            return "No README provided."
        
        # Take the first 700 characters
        summary = readme_content[:700].strip()
        if len(readme_content) > 700:
            summary += "..."
            
        return summary

    def build_file_prompt(
        self,
        file_path: str,
        file_content: str,
        issues: List[Dict],
        project_context: str
    ) -> str:
        """
        Builds the detailed prompt for reviewing a specific file.

        Args:
            file_path (str): The path to the file.
            file_content (str): The content of the file (snippet).
            issues (List[Dict]): List of issues specific to this file.
            project_context (str): The project context summary.

        Returns:
            str: The constructed prompt string.
        """
        
        # Format detected issues for the prompt
        issues_text = ""
        if not issues:
            issues_text = "No critical static analysis issues detected."
        else:
            issues_text = "Static Analysis Detected Issues:\n"
            for issue in issues:
                # Assuming issue structure has at least a message and line number, 
                # adapt based on known structure from Phase 3. 
                # Just dumping the dict as string is safe if keys vary.
                issues_text += f"- {issue}\n"

        prompt = f"""
You are a senior software architect performing a professional code review.

### Project Context
{project_context}

### File to Review
File Name: {file_path}

### Detected Issues (Static Analysis)
{issues_text}

### Code Snippet (Partial Content)
```python
{file_content}
```

### Instructions
Analyze the provided code and issues. Do NOT rewrite the code. Provide high-level, industry-standard improvement recommendations in the following structured format:

1. **Design Issues**: Architecture patterns, coupling, cohesion.
2. **Code Quality Improvements**: Readability, maintainability, best practices.
3. **Security Recommendations**: Vulnerabilities, input validation, authentications.
4. **Performance Improvements**: Efficiency, complexity, resource usage.
5. **Testing Suggestions**: Unit test coverage cases, edge cases.
"""
        return prompt.strip()
