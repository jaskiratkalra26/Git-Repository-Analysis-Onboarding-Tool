import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
from services.orchestrator_service import OrchestratorService

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    # 1. Get Authentication Token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN environment variable is not set.")
        print("Please set the GITHUB_TOKEN environment variable.")
        return

    orchestrator = OrchestratorService()

    try:
        # 2. Authenticate and List Repositories
        print("\nAuthenticating and fetching repositories...")
        repos = await orchestrator.authenticate_and_get_repos(token)
        
        if not repos:
            print("No repositories found or authentication failed.")
            return

        print("\nAvailable Repositories:")
        print("-" * 60)
        print(f"{'ID':<12} | {'Name'}")
        print("-" * 60)
        
        # Sort repos by name for easier reading
        sorted_repos = sorted(repos, key=lambda x: x.get("name", "").lower())
        
        for repo in sorted_repos:
            r_id = repo.get("id")
            r_name = repo.get("full_name") or repo.get("name")
            print(f"{r_id:<12} | {r_name}")
        print("-" * 60)

        # 3. Get User Selection
        while True:
            repo_id_input = input("\nEnter the Repository ID to analyze (or 'q' to quit): ").strip()
            if repo_id_input.lower() == 'q':
                print("Exiting.")
                return
            
            if not repo_id_input.isdigit():
                print("Invalid input. Please enter a numeric Repository ID.")
                continue
                
            repo_id = int(repo_id_input)
            break

        # 4. Run the Pipeline
        print(f"\nStarting analysis pipeline for Repo ID: {repo_id}...")
        result = await orchestrator.generate_project_report(token, repo_id)

        # 5. Output Results
        if result:
            import json
            print("\n" + "="*50)
            print("PIPELINE EXECUTION SUCCESSFUL")
            print("="*50)
            
            # Save to JSON file
            output_filename = f"analysis_result_{repo_id}.json"
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, default=str)
            
            print(f"Full analysis result saved to: {output_filename}")
            print("="*50)
        else:
            print("\nPipeline execution returned no results.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
